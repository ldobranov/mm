<!-- filepath: frontend/src/views/Login.vue -->
<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">Login</h2>
      <form @submit.prevent="login" class="p-4 border rounded">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input v-model="username" id="username" class="form-control" placeholder="Username" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input v-model="password" id="password" type="password" class="form-control" placeholder="Password" required />
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
      </form>
      <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://192.168.1.77:8000/api/v1/users/login', {
          username: this.username,
          password: this.password
        })
        localStorage.setItem('token', res.data.access_token)
        this.$emit('loggedIn');
        this.$router.push('/profile') // or wherever you want to redirect
      } catch (err) {
        this.error = 'Invalid credentials'
      }
    }
  }
}
</script>