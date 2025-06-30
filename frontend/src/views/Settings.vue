<template>
  <div class="settings-page">
    <h1 class="mb-4">Site Settings</h1>
    <div class="settings-form card shadow-sm p-4 mb-5 bg-white rounded">
      <form @submit.prevent="saveSettings">
        <div class="mb-3">
          <label class="form-label">Languages</label>
          <div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" id="lang-en" value="en" v-model="settings.languages">
              <label class="form-check-label" for="lang-en">English</label>
            </div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" id="lang-bg" value="bg" v-model="settings.languages">
              <label class="form-check-label" for="lang-bg">Bulgarian</label>
            </div>
          </div>
        </div>
        <div class="mb-3" v-for="lang in settings.languages" :key="lang">
          <label :for="'siteName-' + lang" class="form-label">Site Name ({{ lang.toUpperCase() }})</label>
          <input v-model="settings.siteName[lang]" :id="'siteName-' + lang" class="form-control" required />
        </div>
        <div class="mb-3" v-for="lang in settings.languages" :key="'content-' + lang">
          <label :for="'siteContent-' + lang" class="form-label">Home Page Content (HTML, {{ lang.toUpperCase() }})</label>
          <textarea v-model="settings.siteContent[lang]" :id="'siteContent-' + lang" class="form-control" rows="6" placeholder="&lt;h1&gt;Welcome!&lt;/h1&gt; ..."></textarea>
        </div>
        <div class="d-flex flex-wrap gap-2 mt-4">
          <button type="submit" class="btn btn-primary">Save</button>
          <button class="btn btn-success" @click.prevent="saveSettings">Save All Settings</button>
          <span v-if="message" :class="['ms-3', messageType === 'success' ? 'text-success' : 'text-danger']">{{ message }}</span>
        </div>
      </form>
    </div>
    <div class="menu-editor-section card shadow-sm p-4 bg-white rounded">
      <h3 class="mb-4">Menu Editor</h3>
      <DynamicMenuEditor
        :menu="settings.menu"
        :languages="settings.languages"
        @update="onMenuUpdate"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';
import DynamicMenuEditor from '../components/DynamicMenuEditor.vue';
export default {
  name: 'Settings',
  components: { DynamicMenuEditor },
  data() {
    return {
      settings: {
        languages: ["en"],
        siteName: { en: "" },
        siteContent: { en: "" },
        menu: [],
      },
      message: '',
      messageType: '',
    };
  },
  created() {
    this.fetchSettings();
  },
  methods: {
    async fetchSettings() {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/settings`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.settings = response.data;
        // fallback for old settings
        if (!this.settings.languages) this.settings.languages = ["en"];
        if (!this.settings.siteName) this.settings.siteName = { en: "" };
        if (!this.settings.siteContent) this.settings.siteContent = { en: "" };
      } catch (error) {
        this.message = 'Error loading settings';
        this.messageType = 'error';
      }
    },
    async saveSettings() {
      try {
        const payload = {
          ...this.settings,
          menu: JSON.parse(JSON.stringify(this.settings.menu))
        };
        console.log('Saving settings payload:', payload); // Debug log
        await axios.put(`${API_BASE_URL}/api/v1/settings`, payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.message = 'Settings saved!';
        this.messageType = 'success';
        this.$emit('settings-updated', { ...this.settings });
      } catch (error) {
        this.message = 'Error saving settings';
        this.messageType = 'error';
      }
    },
    onMenuUpdate(newMenu) {
      // Only update if changed to avoid infinite loop
      if (JSON.stringify(this.settings.menu) !== JSON.stringify(newMenu)) {
        this.settings.menu = newMenu;
      }
    },
  },
};
</script>

<style scoped>
.settings-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 0 32px 0;
}
.settings-form {
  margin-bottom: 40px;
}
.menu-editor-section {
  margin-bottom: 40px;
}
.card {
  border-radius: 12px;
  border: 1px solid #e3e3e3;
}
</style>
