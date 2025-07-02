<template>
  <div class="widget-admin">
    <h1>Widget Manager</h1>
    <form @submit.prevent="uploadWidget" style="margin-bottom: 2em;">
      <input type="file" @change="onFileChange" accept=".zip" />
      <button type="submit">Upload Widget (.zip)</button>
      <span v-if="uploadError" style="color:red;">{{ uploadError }}</span>
      <span v-if="uploadSuccess" style="color:green;">{{ uploadSuccess }}</span>
    </form>
    <div v-if="loading">Loading widgets...</div>
    <div v-else>
      <div v-for="widget in availableWidgets" :key="widget" class="widget-card">
        <h2>{{ widget }}</h2>
        <button @click="deleteWidget(widget)">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: "WidgetsAdmin",
  data() {
    return {
      widgets: [],
      availableWidgets: [],
      loading: true,
      editingWidget: null,
      templateContent: "",
      file: null,
      uploadError: '',
      uploadSuccess: '',
      availableTypes: [],
    };
  },
  methods: {
    async fetchAvailableWidgets() {
      this.loading = true;
      try {
        const res = await axios.get('/api/v1/widgets/available');
        this.availableWidgets = res.data.widgets;
      } catch (e) {
        this.uploadError = e.response?.data?.detail || e.message;
      } finally {
        this.loading = false;
      }
    },
    async fetchAvailableTypes() {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/v1/widgets/available`);
        this.availableTypes = res.data.widgets || [];
      } catch (e) {
        this.availableTypes = ['clock', 'date', 'temp', 'hive'];
      }
    },
    onFileChange(e) {
      this.file = e.target.files[0];
    },
    async uploadWidget() {
      if (!this.file) return;
      const formData = new FormData();
      formData.append('file', this.file);
      this.uploadError = '';
      this.uploadSuccess = '';
      try {
        // Try modern widget zip install endpoint first
        await axios.post('/api/v1/widgets/install_full_zip_modern', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.uploadSuccess = 'Widget (modern frontend+backend) uploaded!';
        this.fetchAvailableWidgets();
      } catch (e) {
        // Fallback to legacy full widget zip install if modern fails
        try {
          await axios.post('/api/v1/widgets/install_full_zip', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          this.uploadSuccess = 'Widget (legacy frontend+backend) uploaded!';
          this.fetchAvailableWidgets();
        } catch (e2) {
          // Fallback to frontend-only upload if both full installs fail
          try {
            await axios.post('/api/v1/widgets/upload', formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
            this.uploadSuccess = 'Frontend widget uploaded!';
            this.fetchAvailableWidgets();
          } catch (e3) {
            this.uploadError = e3.response?.data?.detail || e3.message;
          }
        }
      }
    },
    async deleteWidget(widget) {
      this.uploadError = '';
      this.uploadSuccess = '';
      if (!confirm(`Delete widget '${widget}'? This cannot be undone.`)) return;
      try {
        await axios.delete(`/api/v1/widgets/available/${widget}`);
        this.uploadSuccess = 'Widget deleted!';
        this.fetchAvailableWidgets();
      } catch (e) {
        this.uploadError = e.response?.data?.detail || e.message;
      }
    },
    async fetchWidgets() {
      // For demo, hardcode widget list. In production, fetch from backend.
      const widgetNames = ["hive"];
      const widgets = [];
      for (const name of widgetNames) {
        const meta = await fetch(`/widgets/${name}/meta`).then(r => r.json());
        widgets.push({ name, meta });
      }
      this.widgets = widgets;
      this.loading = false;
    },
    async toggleWidget(widget) {
      await fetch(`/widgets/${widget.name}/meta`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(widget.meta),
      });
    },
    async editTemplate(widget) {
      const res = await fetch(`/widgets/${widget.name}/template`).then(r => r.json());
      this.templateContent = res.content;
      this.editingWidget = widget.name;
    },
    async saveTemplate(widget) {
      await fetch(`/widgets/${widget.name}/template`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: this.templateContent }),
      });
      this.editingWidget = null;
    },
    cancelEdit() {
      this.editingWidget = null;
      this.templateContent = "";
    },
  },
  async mounted() {
    await this.fetchWidgets();
    await this.fetchAvailableTypes();
  },
};
</script>

<style scoped>
.widget-admin {
  max-width: 800px;
  margin: 0 auto;
}
.widget-card {
  border: 1px solid #ccc;
  padding: 1em;
  margin-bottom: 1em;
  border-radius: 8px;
}
</style>
