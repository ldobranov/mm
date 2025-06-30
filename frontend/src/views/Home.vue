<template>
  <div class="home">
    <h1>{{ siteName }}</h1>
    <div v-html="siteContent"></div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';
export default {
  name: 'Home',
  data() {
    return {
      siteName: '',
      siteContent: '',
      languages: ["en"],
      lang: localStorage.getItem('lang') || 'en',
    };
  },
  watch: {
    lang(newLang) {
      this.updateContent(newLang);
    }
  },
  async created() {
    await this.loadSettings();
    window.addEventListener('storage', this.onLangChange);
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.onLangChange);
  },
  methods: {
    async loadSettings() {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/settings`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.languages = response.data.languages;
        this.allSiteName = response.data.siteName;
        this.allSiteContent = response.data.siteContent;
        this.updateContent(this.lang);
      } catch (e) {
        // fallback to defaults
      }
    },
    updateContent(lang) {
      this.siteName = (this.allSiteName && this.allSiteName[lang]) || (this.allSiteName && this.allSiteName['en']) || '';
      this.siteContent = (this.allSiteContent && this.allSiteContent[lang]) || (this.allSiteContent && this.allSiteContent['en']) || '';
    },
    onLangChange(e) {
      if (e.key === 'lang') {
        this.lang = localStorage.getItem('lang') || 'en';
      }
    },
    async onSettingsUpdated(newSettings) {
      // Update languages and content live if settings change
      this.languages = newSettings.languages || ["en"];
      this.allSiteName = newSettings.siteName;
      this.allSiteContent = newSettings.siteContent;
      this.updateContent(this.lang);
    }
  },
};
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 50px;
}
</style>