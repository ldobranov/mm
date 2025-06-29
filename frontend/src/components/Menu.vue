<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">{{ menuToRender.length ? menuToRender[0].label[lang] || menuToRender[0].label['en'] : 'Vending Machine' }}</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <template v-for="item in menuToRender" :key="item.id">
            <li v-if="checkVisibility(item)" class="nav-item" :class="{ dropdown: item.children && item.children.length }">
              <router-link v-if="!item.children || !item.children.length" class="nav-link" :to="item.route">{{ item.label[lang] || item.label['en'] }}</router-link>
              <div v-else class="nav-link dropdown-toggle" data-bs-toggle="dropdown" role="button" aria-expanded="false">{{ item.label[lang] || item.label['en'] }}</div>
              <ul v-if="item.children && item.children.length" class="dropdown-menu">
                <li v-for="sub in item.children" :key="sub.id" v-if="checkVisibility(sub)">
                  <router-link v-if="!sub.children || !sub.children.length" class="dropdown-item" :to="sub.route">{{ sub.label[lang] || sub.label['en'] }}</router-link>
                  <div v-else class="dropdown-item dropdown-toggle">{{ sub.label[lang] || sub.label['en'] }}</div>
                  <ul v-if="sub.children && sub.children.length" class="dropdown-menu">
                    <li v-for="sub2 in sub.children" :key="sub2.id" v-if="checkVisibility(sub2)">
                      <router-link class="dropdown-item" :to="sub2.route">{{ sub2.label[lang] || sub2.label['en'] }}</router-link>
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </template>
        </ul>
        <ul class="navbar-nav">
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <router-link class="nav-link" to="/profile">Profile</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from 'axios';
export default {
  name: 'Menu',
  props: {
    menu: { type: Array, default: null },
    languages: { type: Array, default: () => ["en"] },
    lang: { type: String, default: 'en' },
  },
  data() {
    return {
      loggedIn: !!localStorage.getItem('token'),
      dynamicMenu: [],
    };
  },
  computed: {
    isLoggedIn() {
      return this.loggedIn;
    },
    isAdmin() {
      const token = localStorage.getItem('token');
      if (!token) return false;
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role === 'admin';
      } catch (e) {
        return false;
      }
    },
    menuToRender() {
      // Use prop if passed, else fallback to dynamicMenu
      return this.menu || this.dynamicMenu;
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      this.loggedIn = false;
      this.$router.push('/login');
    },
    updateAuth() {
      this.loggedIn = !!localStorage.getItem('token');
    },
    async fetchMenu() {
      try {
        const response = await axios.get('/api/v1/settings', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.dynamicMenu = response.data.menu || [];
      } catch (e) {
        this.dynamicMenu = [];
      }
    },
    checkVisibility(item) {
      if (item.visibility === 'admin') return this.isAdmin;
      if (item.visibility === 'registered') return this.isLoggedIn;
      return true;
    }
  },
  async created() {
    if (!this.menu) await this.fetchMenu();
    window.addEventListener('storage', this.updateAuth);
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.updateAuth);
  }
}
</script>

<style scoped>
.navbar-brand {
  font-weight: bold;
}

.nav-link {
  color: white;
}

.nav-link:hover {
  color: #f8f9fa;
}

.router-link-exact-active {
  color: #f8f9fa !important;
  font-weight: bold;
}
</style>