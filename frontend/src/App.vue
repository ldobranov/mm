<template>
  <Header :siteName="siteName" />
  <Menu
    :key="componentKey"
    :menu="menu"
    :languages="languages"
    :lang="currentLang"
    :siteName="siteName"
  />
  <div class="lang-switcher" v-if="languages.length > 1" style="text-align:right; margin: 10px 20px 0 0;">
    <button v-for="lang in languages" :key="lang" @click="setLang(lang)">{{ lang.toUpperCase() }}</button>
  </div>
  <router-view @loggedIn="forceRerender" @settings-updated="onSettingsUpdated" />
  <Footer :siteName="siteName" />
</template>

<script>
import Menu from './components/Menu.vue'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

export default {
  name: 'App',
  components: {
    Menu,
    Header,
    Footer,
  },
  data() {
    return {
      componentKey: 0,
      languages: ["en"],
      menu: [],
      currentLang: localStorage.getItem('lang') || 'en',
      siteName: "App",
      siteNameObj: {},
    };
  },
  async created() {
    try {
      const response = await axios.get('/api/v1/settings', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      this.languages = response.data.languages || ["en"];
      this.menu = response.data.menu || [];
      this.siteNameObj = response.data.siteName || {};
      this.updateSiteName();
    } catch (e) {
      this.languages = ["en"];
      this.menu = [];
      this.siteNameObj = { en: "App" };
      this.updateSiteName();
    }
    if (!localStorage.getItem('lang')) {
      localStorage.setItem('lang', this.languages[0]);
    }
  },
  setup() {
    const { locale } = useI18n();
    return { locale };
  },
  methods: {
    forceRerender() {
      this.componentKey += 1;
    },
    setLang(lang) {
      this.locale = lang;
      localStorage.setItem('lang', lang);
      this.currentLang = lang;
      this.updateSiteName();
      this.forceRerender();
    },
    async onSettingsUpdated(newSettings) {
      this.languages = newSettings.languages || ["en"];
      this.menu = newSettings.menu || [];
      this.siteNameObj = newSettings.siteName || {};
      this.updateSiteName();
      this.forceRerender();
    },
    updateSiteName() {
      // Use the current language, fallback to 'en', then to "App"
      const name = this.siteNameObj[this.currentLang] || this.siteNameObj.en || "App";
      this.siteName = name;
      document.title = name;
    }
  },
}
</script>