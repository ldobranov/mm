<template>
  <div>
    <h1 class="mb-4">User Management</h1>
    <ul class="list-group">
      <li v-for="(user, idx) in users" :key="user.id" class="list-group-item">
        <div v-if="editIndex === idx" class="d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ user.username }}</strong> - {{ user.email }}
          </div>
          <div class="d-flex align-items-center">
            <select v-model="editUser.role" class="form-select form-select-sm me-2" style="width: auto;">
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
            <button @click="updateUserRole(user)" class="btn btn-success btn-sm me-2">Save</button>
            <button @click="cancelEdit" class="btn btn-secondary btn-sm">Cancel</button>
          </div>
        </div>
        <div v-else class="d-flex justify-content-between align-items-center w-100">
          <div>
            <strong>{{ user.username }}</strong> - {{ user.email }} - <span class="badge bg-primary">{{ user.role }}</span>
          </div>
          <div>
            <button @click="startEdit(idx, user)" class="btn btn-warning btn-sm me-2">Edit Role</button>
            <button @click="deleteUser(user)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Users',
  data() {
    return {
      users: [],
      editIndex: null,
      editUser: { role: '' },
    };
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get('/api/v1/users/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },
    startEdit(idx, user) {
      this.editIndex = idx;
      this.editUser = { ...user };
    },
    cancelEdit() {
      this.editIndex = null;
      this.editUser = { role: '' };
    },
    async updateUserRole(user) {
      try {
        await axios.put(`/api/v1/users/${user.id}`, { role: this.editUser.role }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.cancelEdit();
        this.fetchUsers();
      } catch (error) {
        console.error('Error updating user role:', error);
      }
    },
    async deleteUser(user) {
      try {
        await axios.delete(`/api/v1/users/${user.id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.users = this.users.filter(u => u.id !== user.id);
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    },
  },
};
</script>