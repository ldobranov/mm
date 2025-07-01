<template>
  <div>
    <h2>Schedules</h2>
    <button class="btn btn-primary mb-3" @click="showAdd = true">Add Schedule</button>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Widget</th>
          <th>Action</th>
          <th>Time</th>
          <th>Repeat</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sched in schedules" :key="sched.id" :class="{ 'table-secondary': isScheduleComplete(sched) }">
          <td>{{ sched.id }}</td>
          <td>{{ widgetName(sched.widget_id) }}</td>
          <td>{{ sched.action }}</td>
          <td>{{ sched.time }}</td>
          <td>{{ sched.repeat || 'once' }}</td>
          <td>
            <button class="btn btn-sm btn-danger" @click="deleteSchedule(sched.id)">Delete</button>
            <button class="btn btn-sm btn-warning" @click="editSchedule(sched)">Edit</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showAdd" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-dialog" @click.stop>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h4>{{ editId ? 'Edit Schedule' : 'Add Schedule' }}</h4>
          <button class="btn-close" @click="closeModal" aria-label="Close" style="font-size:1.5rem;background:none;border:none;">&times;</button>
        </div>
        <div class="mb-2">
          <label>Widget:</label>
          <select v-model.number="form.widget_id" class="form-control">
            <option disabled :value="null">Select widget</option>
            <option v-for="w in widgets" :value="w.id" :key="w.id">{{ widgetName(w.id) }}</option>
          </select>
        </div>
        <div class="mb-2">
          <label>Action:</label>
          <select v-model="form.action" class="form-control" :disabled="!form.widget_id">
            <option disabled value="">Select action</option>
            <option v-for="a in availableActions" :value="a.value" :key="a.value">{{ a.label }}</option>
          </select>
        </div>
        <div class="mb-2">
          <label>Time:</label>
          <input v-model="form.time" type="datetime-local" class="form-control" />
        </div>
        <div class="mb-2">
          <label>Repeat:</label>
          <select v-model="form.repeat" class="form-control">
            <option value="once">Once</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
        <button class="btn btn-primary me-2" @click="editId ? updateSchedule() : addSchedule()" :disabled="!form.widget_id || !form.action || !form.time">{{ editId ? 'Update' : 'Add' }}</button>
        <button class="btn btn-secondary" @click="closeModal">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '../config'
export default {
  name: 'Schedules',
  data() {
    return {
      schedules: [],
      widgets: [],
      showAdd: false,
      editId: null,
      form: {
        widget_id: null,
        action: '',
        time: '',
        repeat: 'once',
      },
    }
  },
  computed: {
    availableActions() {
      const w = this.widgets.find(w => w.id === this.form.widget_id)
      if (!w) return []
      // Define actions per widget type
      if (w.type === 'hive') {
        return [
          { value: 'miners/start', label: 'Start Miner' },
          { value: 'miners/stop', label: 'Stop Miner' },
          { value: 'shutdown', label: 'Shutdown' },
          { value: 'enable', label: 'Enable' },
          { value: 'disable', label: 'Disable' },
        ]
      }
      if (w.type === 'clock' || w.type === 'date' || w.type === 'temp') {
        return [
          { value: 'enable', label: 'Enable' },
          { value: 'disable', label: 'Disable' },
        ]
      }
      // Add more widget types and their actions here as needed
      return []
    }
  },
  async mounted() {
    await this.fetchSchedules()
    await this.fetchWidgets()
    this.widgetInterval = setInterval(this.fetchWidgets, 10000) // poll every 10s
  },
  beforeUnmount() {
    if (this.widgetInterval) clearInterval(this.widgetInterval)
  },
  methods: {
    isScheduleComplete(sched) {
      // If not repeating and time is in the past, mark as complete
      if (!sched.repeat || sched.repeat === 'once') {
        const now = new Date();
        const schedTime = new Date(sched.time);
        return schedTime < now;
      }
      return false;
    },
    async fetchSchedules() {
      const res = await axios.get(`${API_BASE_URL}/api/v1/schedules/`)
      this.schedules = res.data
    },
    async fetchWidgets() {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/v1/widgets/`)
        const widgets = res.data.map((widget, idx) => ({
          id: widget.id !== undefined ? widget.id : idx,
          type: widget.type,
          name: widget.name || widget.type // prefer name, fallback to type
        }))
        this.widgets = widgets
      } catch (error) {
        console.error('Error fetching widgets:', error)
      }
    },
    async addSchedule() {
      try {
        // Convert local time to UTC ISO string
        const local = new Date(this.form.time)
        const utcIso = local.toISOString() // always UTC
        const payload = { ...this.form, widget_id: Number(this.form.widget_id), time: utcIso };
        await axios.post(`${API_BASE_URL}/api/v1/schedules/`, payload)
        this.closeModal()
        await this.fetchSchedules()
      } catch (e) {
        alert('Failed to add schedule: ' + (e?.message || e))
      }
    },
    async updateSchedule() {
      try {
        // Convert local time to UTC ISO string
        const local = new Date(this.form.time)
        const utcIso = local.toISOString() // always UTC
        const payload = { ...this.form, widget_id: Number(this.form.widget_id), time: utcIso };
        await axios.put(`${API_BASE_URL}/api/v1/schedules/${this.editId}`, payload)
        this.closeModal()
        await this.fetchSchedules()
      } catch (e) {
        alert('Failed to update schedule: ' + (e?.message || e))
      }
    },
    editSchedule(sched) {
      this.form = { ...sched, widget_id: Number(sched.widget_id) }
      this.editId = sched.id
      this.showAdd = true
    },
    async deleteSchedule(id) {
      if (!confirm('Delete this schedule?')) return
      try {
        await axios.delete(`${API_BASE_URL}/api/v1/schedules/${id}`)
        await this.fetchSchedules()
      } catch (e) {
        alert('Failed to delete schedule: ' + (e?.message || e))
      }
    },
    closeModal() {
      this.showAdd = false;
      this.editId = null;
      this.form = { widget_id: null, action: '', time: '', repeat: 'once' };
    },
    widgetName(id) {
      const w = this.widgets.find(w => w.id === id)
      return w ? `${w.name} #${w.id}` : `Widget ${id}`
    }
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}
.modal-dialog {
  min-width: 350px;
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.18);
  pointer-events: auto;
}
</style>
