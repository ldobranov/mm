<template>
  <div class="widget-admin">
    <h1>Widget Manager</h1>
    <div v-if="loading">Loading widgets...</div>
    <div v-else>
      <div v-for="widget in widgets" :key="widget.name" class="widget-card">
        <h2>{{ widget.meta.name }}</h2>
        <p>{{ widget.meta.description }}</p>
        <label>
          <input type="checkbox" v-model="widget.meta.enabled" @change="toggleWidget(widget)" />
          Enabled
        </label>
        <button @click="editTemplate(widget)">Edit Template</button>
        <div v-if="editingWidget === widget.name">
          <textarea v-model="templateContent" rows="10" cols="60"></textarea>
          <br />
          <button @click="saveTemplate(widget)">Save Template</button>
          <button @click="cancelEdit">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "WidgetsAdmin",
  data() {
    return {
      widgets: [],
      loading: true,
      editingWidget: null,
      templateContent: "",
    };
  },
  methods: {
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
  mounted() {
    this.fetchWidgets();
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
