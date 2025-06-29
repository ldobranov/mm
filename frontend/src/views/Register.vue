<!-- filepath: frontend/src/views/Register.vue -->
<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">Register</h2>
      <form @submit.prevent="register" class="p-4 border rounded">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input v-model="username" id="username" class="form-control" placeholder="Username" required />
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input v-model="email" id="email" type="email" class="form-control" placeholder="Email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input v-model="password" id="password" type="password" class="form-control" placeholder="Password" required />
        </div>
        <button type="submit" class="btn btn-primary">Register</button>
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
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async register() {
      try {
        await axios.post('http://192.168.1.77:8000/api/v1/users/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })
        this.$router.push('/login')
      } catch (err) {
        this.error = 'Registration failed'
      }
    }
  }
}
</script>