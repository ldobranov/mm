<template>
  <div>
    <h2>Widgets</h2>
    <button class="btn btn-primary mb-3" @click="showAdd = true">Add Widget</button>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Type</th>
          <th>Enabled</th>
          <th>Config</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="widget in widgets" :key="widget.id">
          <td>{{ widget.id }}</td>
          <td>{{ widget.type }}</td>
          <td>
            <input type="checkbox" v-model="widget.enabled" @change="updateWidget(widget)" />
          </td>
          <td>
            <span v-if="widget.type === 'clock'">
              Style: {{ widget.config?.style || 'digital' }}
            </span>
            <span v-else-if="widget.type === 'date'">
              Format: {{ widget.config?.format || 'YYYY-MM-DD' }}
            </span>
            <span v-else-if="widget.type === 'temp'">
              (No config)
            </span>
            <span v-else-if="widget.type === 'hive'">
              HiveOS Rig
            </span>
          </td>
          <td>
            <button class="btn btn-sm btn-warning me-2" @click="editWidget(widget)">Edit</button>
            <button class="btn btn-sm btn-danger" @click="deleteWidget(widget.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Add/Edit Widget Modal -->
    <div v-if="showAdd || showEdit" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ showAdd ? 'Add' : 'Edit' }} Widget</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="showAdd ? addWidget() : saveEdit()">
              <div class="mb-3">
                <label class="form-label">Type</label>
                <select v-model="form.type" class="form-select" :disabled="showEdit">
                  <option value="clock">Clock</option>
                  <option value="date">Date</option>
                  <option value="temp">Temp</option>
                  <option value="hive">HiveOS Rig</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Enabled</label>
                <input type="checkbox" v-model="form.enabled" />
              </div>
              <div v-if="form.type === 'clock'" class="mb-3">
                <label class="form-label">Style</label>
                <select v-model="form.config.style" class="form-select">
                  <option value="digital">Digital</option>
                  <option value="circle">Circle</option>
                </select>
              </div>
              <div v-if="form.type === 'date'" class="mb-3">
                <label class="form-label">Format</label>
                <input v-model="form.config.format" class="form-control" placeholder="YYYY-MM-DD" />
              </div>
              <div v-if="form.type === 'hive'" class="mb-3">
                <label class="form-label">API Token</label>
                <input v-model="form.config.token" class="form-control" placeholder="HiveOS API Token" />
                <label class="form-label mt-2">Farm ID</label>
                <input v-model="form.config.farmId" class="form-control" placeholder="Farm ID" />
                <label class="form-label mt-2">Worker ID</label>
                <input v-model="form.config.workerId" class="form-control" placeholder="Worker ID" />
              </div>
              <!-- Temp has no config for now -->
              <button type="submit" class="btn btn-success">Save</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Widget',
  data() {
    return {
      widgets: [],
      showAdd: false,
      showEdit: false,
      form: {
        type: 'clock',
        enabled: true,
        config: {},
      },
      editId: null,
    }
  },
  async mounted() {
    await this.fetchWidgets()
  },
  methods: {
    async fetchWidgets() {
      try {
        const res = await axios.get('/api/v1/widgets/')
        this.widgets = res.data
      } catch (e) {
        alert('Failed to fetch widgets: ' + (e?.message || e))
      }
    },
    async addWidget() {
      const payload = { ...this.form }
      if (payload.type === 'clock') {
        payload.config = { style: payload.config.style || 'digital' }
      } else if (payload.type === 'date') {
        payload.config = { format: payload.config.format || 'YYYY-MM-DD' }
      } else if (payload.type === 'hive') {
        payload.config = {
          token: payload.config.token || '',
          farmId: payload.config.farmId || '',
          workerId: payload.config.workerId || ''
        }
      } else {
        payload.config = {}
      }
      try {
        await axios.post('/api/v1/widgets/', payload)
      } catch (e) {
        alert('Failed to add widget: ' + (e?.message || e))
      }
      this.closeModal()
      await this.fetchWidgets()
    },
    editWidget(widget) {
      this.showEdit = true
      this.editId = widget.id
      this.form = JSON.parse(JSON.stringify(widget))
    },
    async saveEdit() {
      const payload = { ...this.form }
      if (payload.type === 'clock') {
        payload.config = { style: payload.config.style || 'digital' }
      } else if (payload.type === 'date') {
        payload.config = { format: payload.config.format || 'YYYY-MM-DD' }
      } else if (payload.type === 'hive') {
        payload.config = {
          token: payload.config.token || '',
          farmId: payload.config.farmId || '',
          workerId: payload.config.workerId || ''
        }
      } else {
        payload.config = {}
      }
      try {
        await axios.put(`/api/v1/widgets/${this.editId}`, payload)
      } catch (e) {
        alert('Failed to update widget: ' + (e?.message || e))
      }
      this.closeModal()
      await this.fetchWidgets()
    },
    async updateWidget(widget) {
      // Only update enabled/config
      const payload = { ...widget }
      try {
        await axios.put(`/api/v1/widgets/${widget.id}`, payload)
      } catch (e) {
        alert('Failed to update widget: ' + (e?.message || e))
      }
      await this.fetchWidgets()
    },
    async deleteWidget(id) {
      if (!confirm('Delete this widget?')) return
      try {
        await axios.delete(`/api/v1/widgets/${id}`)
      } catch (e) {
        alert('Failed to delete widget: ' + (e?.message || e))
      }
      await this.fetchWidgets()
    },
    closeModal() {
      this.showAdd = false
      this.showEdit = false
      this.editId = null
      this.form = { type: 'clock', enabled: true, config: {} }
    },
  },
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
}
.modal-dialog {
  min-width: 350px;
}
</style>
