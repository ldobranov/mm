import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Items from '../views/catalogue/items.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import Users from '../views/Users.vue'
import Categories from '../views/Categories.vue'
import Settings from '../views/Settings.vue'
import Display from '../views/Display.vue'
import Widget from '../views/Widget.vue'
import Schedules from '../views/Schedules.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/items', name: 'Items', component: Items },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/users', name: 'Users', component: Users },
  { path: '/categories', name: 'Categories', component: Categories },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/display', name: 'Display', component: Display },
  { path: '/widget', name: 'Widget', component: Widget },
  { path: '/schedules', name: 'Schedules', component: Schedules },
  // Add more routes here as needed
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router