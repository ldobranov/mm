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
          <td style="max-width: 100%; word-break: break-all; white-space: pre-line; overflow-x: auto;">
            <span v-if="widget.type === 'clock'">
              Style: {{ widget.config?.style || 'digital' }}
            </span>
            <span v-else-if="widget.type === 'date'">
              Format: {{ widget.config?.format || 'YYYY-MM-DD' }}
            </span>
            <span v-else-if="widget.type === 'temp'">
              (No config)
            </span>
            <span v-else>
              <span v-if="widget.config && Object.keys(widget.config).length">
                <span v-for="(val, key) in widget.config" :key="key">
                  <b>{{ key }}:</b> {{ val }}<br>
                </span>
              </span>
              <span v-else>
                (No config)
              </span>
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
            <form @submit.prevent="showAdd ? addWidget() : saveEdit()" :style="{ background: '#f8f9fa', borderRadius: '8px', padding: '16px' }">
              <div class="mb-3">
                <label class="form-label">Type</label>
                <select v-model="form.type" class="form-select" :disabled="showEdit">
                  <option v-for="(meta, type) in widgetMetas" :key="type" :value="type">{{ meta.name || type }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Enabled</label>
                <input type="checkbox" v-model="form.enabled" />
              </div>
              <template v-for="field in getFieldsForType(form.type)" :key="field.name">
                <div class="mb-3" v-if="!field.showIf || Object.entries(field.showIf).every(([k,v]) => form.config[k] === v)">
                  <label class="form-label">{{ field.label }}</label>
                  <select v-if="field.type === 'select'" v-model="form.config[field.name]" class="form-select">
                    <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                  <input v-else-if="field.type === 'text'" v-model="form.config[field.name]" class="form-control" :placeholder="field.placeholder || ''" />
                  <!-- Add more field types as needed -->
                </div>
              </template>
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
import { API_BASE_URL } from '../config'
import ClockWidget from '../widgets/ClockWidget.vue'
import DateWidget from '../widgets/DateWidget.vue'
import TempWidget from '../widgets/TempWidget.vue'
import { defineAsyncComponent } from 'vue'

export default {
  name: 'Widget',
  components: {
    ClockWidget,
    DateWidget,
    TempWidget
  },
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
      widgetMetas: {}, // { type: meta }
      loadingMetas: false,
    }
  },
  async mounted() {
    await this.fetchWidgets()
    await this.loadWidgetMetas()
  },
  methods: {
    async fetchWidgets() {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/v1/widgets/`)
        this.widgets = res.data
      } catch (e) {
        alert('Failed to fetch widgets: ' + (e?.message || e))
      }
    },
    async loadWidgetMetas() {
      this.loadingMetas = true;
      const types = ['clock', 'date', 'temp', 'hive']; // TODO: fetch dynamically
      const metas = {};
      for (const type of types) {
        try {
          // CHANGED: fetch meta from /widgets/{type}.json
          const meta = await fetch(`/widgets/${type}.json`).then(r => r.json());
          metas[type] = meta;
        } catch (e) {
          // fallback for built-ins
          if (type === 'clock') metas.clock = { fields: [ { name: 'style', label: 'Style', type: 'select', options: [ {label:'Digital',value:'digital'}, {label:'Circle',value:'circle'} ], default: 'digital' } ] };
          if (type === 'date') metas.date = { fields: [ { name: 'format', label: 'Format', type: 'text', placeholder: 'YYYY-MM-DD', default: 'YYYY-MM-DD' } ] };
          if (type === 'temp') metas.temp = { fields: [] };
        }
      }
      console.log('Loaded widgetMetas:', metas);
      this.widgetMetas = metas;
      this.loadingMetas = false;
    },
    getFieldsForType(type) {
      return this.widgetMetas[type]?.fields || [];
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
          workerId: payload.config.workerId || '',
          mode: payload.config.mode || 'rig' // ensure mode is included
        }
      } else {
        payload.config = {}
      }
      try {
        await axios.post(`${API_BASE_URL}/api/v1/widgets/`, payload)
      } catch (e) {
        alert('Failed to add widget: ' + (e?.message || e))
      }
      this.closeModal()
      await this.fetchWidgets()
    },
    editWidget(widget) {
      this.showEdit = true
      this.editId = widget.id
      // Deep copy
      this.form = JSON.parse(JSON.stringify(widget))
      // Ensure all config fields are present for the selected type
      const fields = this.getFieldsForType(widget.type)
      console.log('Editing widget:', widget)
      console.log('Fields for type:', widget.type, fields)
      if (fields && this.form.config) {
        for (const field of fields) {
          if (!(field.name in this.form.config)) {
            this.form.config[field.name] = field.default || ''
          }
        }
      }
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
          workerId: payload.config.workerId || '',
          mode: payload.config.mode || 'rig' // ensure mode is included
        }
      } else {
        payload.config = {}
      }
      try {
        await axios.put(`${API_BASE_URL}/api/v1/widgets/${this.editId}`, payload)
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
        await axios.put(`${API_BASE_URL}/api/v1/widgets/${widget.id}`, payload)
      } catch (e) {
        alert('Failed to update widget: ' + (e?.message || e))
      }
      await this.fetchWidgets()
    },
    async deleteWidget(id) {
      if (!confirm('Delete this widget?')) return
      try {
        await axios.delete(`${API_BASE_URL}/api/v1/widgets/${id}`)
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
    getWidgetComponent(widget) {
      if (widget.type === 'clock') return 'ClockWidget'
      if (widget.type === 'date') return 'DateWidget'
      if (widget.type === 'temp') return 'TempWidget'
      // Dynamic loader for all other widget types, with error handling
      const fileName = widget.type.charAt(0).toUpperCase() + widget.type.slice(1) + 'Widget.vue';
      return defineAsyncComponent({
        loader: () => import(/* @vite-ignore */`../widgets/${fileName}`),
        errorComponent: {
          template: `<div style='color:red;'>Widget not found: ${fileName}</div>`
        },
        loadingComponent: {
          template: '<div>Loading widget...</div>'
        },
        delay: 200,
        timeout: 3000
      });
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

<!-- In the template where you render the widget component: -->
<component
  :is="getWidgetComponent(widget)"
  :widget="widget"
  v-bind="widget.type === 'hive' ? { mode: widget.config?.mode || 'rig' } : {}"
/>
