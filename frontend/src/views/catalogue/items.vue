<template>
  <div>
    <h1 class="mb-4">{{$t('items.title')}}</h1>
    <form @submit.prevent="addItem" class="mb-4 p-3 border rounded">
      <div class="row g-3">
        <div class="col-md-3">
          <input v-model="newItem.name" class="form-control" :placeholder="$t('items.name')" required />
        </div>
        <div class="col-md-2">
          <input v-model="newItem.price" class="form-control" :placeholder="$t('items.price')" type="number" step="0.01" required />
        </div>
        <div class="col-md-4">
          <input v-model="newItem.description" class="form-control" :placeholder="$t('items.description')" />
        </div>
        <div class="col-md-3">
          <select v-model="newItem.category_ids" class="form-select" multiple>
            <option v-for="category in categories.filter(cat => cat.selectable)" :value="category.id" :key="category.id">{{ category.name }}</option>
          </select>
        </div>
        <div class="col-12">
          <button type="submit" class="btn btn-primary">{{$t('items.addItem')}}</button>
        </div>
      </div>
    </form>
    <ul class="list-group">
      <li v-for="(item, idx) in items" :key="item.id" class="list-group-item">
        <div v-if="editIndex === idx" class="p-3 border rounded">
          <div class="row g-3">
            <div class="col-md-3">
              <input v-model="editItem.name" class="form-control" :placeholder="$t('items.name')" required />
            </div>
            <div class="col-md-2">
              <input v-model="editItem.price" class="form-control" :placeholder="$t('items.price')" type="number" step="0.01" required />
            </div>
            <div class="col-md-4">
              <input v-model="editItem.description" class="form-control" :placeholder="$t('items.description')" />
            </div>
            <div class="col-md-3">
              <select v-model="editItem.category_ids" class="form-select" multiple>
                <option v-for="category in categories.filter(cat => cat.selectable)" :value="category.id" :key="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="col-12">
              <button @click="updateItem(item.id)" class="btn btn-success btn-sm me-2">{{$t('items.save')}}</button>
              <button @click="cancelEdit" class="btn btn-secondary btn-sm">{{$t('items.cancel')}}</button>
            </div>
          </div>
        </div>
        <div v-else class="d-flex justify-content-between align-items-center">
          <div>
            <h5>{{ item.name }} - ${{ item.price }}</h5>
            <small class="text-muted">{{ item.description }}</small>
            <div>
              <span v-for="catId in item.categories" :key="catId" class="badge bg-info text-dark me-1">
                {{ getCategoryName(catId) }}
              </span>
            </div>
          </div>
          <div>
            <button @click="startEdit(idx, item)" class="btn btn-warning btn-sm me-2">{{$t('items.edit')}}</button>
            <button @click="deleteItem(item.id)" class="btn btn-danger btn-sm">{{$t('items.delete')}}</button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '../../config'

export default {
  name: 'ItemList',
  data() {
    return {
      items: [],
      categories: [],
      newItem: {
        name: '',
        price: '',
        description: '',
        category_ids: [],
      },
      editIndex: null,
      editItem: { name: '', price: '', description: '', category_ids: [] }
    }
  },
  mounted() {
    this.fetchItems()
    this.fetchCategories()
  },
  methods: {
    fetchItems() {
      axios.get(`${API_BASE_URL}/api/v1/items/`)
        .then(response => {
          this.items = response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    fetchCategories() {
      axios.get(`${API_BASE_URL}/api/v1/categories/`)
        .then(response => {
          this.categories = response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    addItem() {
      axios.post(`${API_BASE_URL}/api/v1/items/`, this.newItem)
        .then(() => {
          this.newItem = { name: '', price: '', description: '', category_ids: [] }
          this.fetchItems()
        })
        .catch(error => {
          console.error(error)
        })
    },
    deleteItem(id) {
      axios.delete(`${API_BASE_URL}/api/v1/items/${id}`)
        .then(() => {
           this.fetchItems()
        })
        .catch(error => {
          console.error(error)
        })
      },
      startEdit(idx, item) {
        this.editIndex = idx
        this.editItem = { ...item, category_ids: [...item.categories] }
      },
      cancelEdit() {
        this.editIndex = null
        this.editItem = { name: '', price: '', description: '', category_ids: [] }
      },
      updateItem(id) {
        axios.put(`${API_BASE_URL}/api/v1/items/${id}`, this.editItem)
          .then(() => {
            this.cancelEdit()
            this.fetchItems()
          })
          .catch(error => {
            console.error(error)
          })
      },
      getCategoryName(catId) {
        const cat = this.categories.find(c => c.id === catId)
        return cat ? cat.name : catId
      }
  }
}
</script>