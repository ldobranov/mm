<!-- filepath: frontend/src/views/Profile.vue -->
<template>
  <div>
    <div class="container mt-4">
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{$t('profile.success')}}</div>
      <div class="row justify-content-center">
        <div class="col-md-6">
          <h2 class="mb-4">{{$t('profile.userProfile')}}</h2>
          <div v-if="user" class="card">
            <div class="card-body">
              <form @submit.prevent="updateProfile">
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.username')}}</strong></label>
                  <input v-model="editUser.username" class="form-control" type="text" />
                </div>
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.email')}}</strong></label>
                  <input v-model="editUser.email" class="form-control" type="email" />
                </div>
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.oldPassword')}}</strong></label>
                  <input v-model="editUser.old_password" class="form-control" type="password" :placeholder="$t('profile.oldPassword')" />
                </div>
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.newPassword')}}</strong></label>
                  <input v-model="editUser.password" class="form-control" type="password" :placeholder="$t('profile.newPassword')" />
                </div>
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.confirmNewPassword')}}</strong></label>
                  <input v-model="editUser.confirm_password" class="form-control" type="password" :placeholder="$t('profile.confirmNewPassword')" />
                </div>
                <div class="mb-3">
                  <label class="form-label"><strong>{{$t('profile.role')}}</strong></label>
                  <input class="form-control" type="text" :value="user.role" disabled />
                </div>
                <button type="submit" class="btn btn-primary">{{$t('profile.saveChanges')}}</button>
              </form>
            </div>
          </div>
          <div v-else class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '../config'

export default {
  data() {
    return {
      user: null,
      editUser: { username: '', email: '', password: '', old_password: '', confirm_password: '' },
      error: '',
      success: false
    }
  },
  mounted() {
    axios.get(`${API_BASE_URL}/api/v1/users/me`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => {
      this.user = res.data
      this.editUser.username = res.data.username
      this.editUser.email = res.data.email
    })
    .catch(() => {
      this.error = 'Not authenticated or session expired.'
    })
  },
  methods: {
    updateProfile() {
      this.error = '';
      this.success = false;
      if (this.editUser.password && this.editUser.password !== this.editUser.confirm_password) {
        this.error = 'New passwords do not match.';
        return;
      }
      const payload = {};
      if (this.editUser.username !== this.user.username) payload.username = this.editUser.username;
      if (this.editUser.email !== this.user.email) payload.email = this.editUser.email;
      if (this.editUser.password) payload.password = this.editUser.password;
      if (this.editUser.old_password) payload.old_password = this.editUser.old_password;
      axios.put(`${API_BASE_URL}/api/v1/users/me`, payload, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      .then(res => {
        this.user = res.data;
        this.success = true;
        this.editUser.password = '';
        this.editUser.old_password = '';
        this.editUser.confirm_password = '';
      })
      .catch(err => {
        this.error = err.response?.data?.detail || 'Update failed.';
      });
    }
  }
}
</script>