<template>
  <div>
    <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger']" role="alert">
      {{ message }}
    </div>
    <h1 class="mb-4">{{$t('categories.title')}}</h1>
    <form @submit.prevent="createCategory" class="mb-4 p-3 border rounded">
      <div class="row g-3 align-items-center">
        <div class="col-auto">
          <input v-model="newCategoryName" class="form-control" :placeholder="$t('categories.newCategoryName')" required />
        </div>
        <div class="col-auto">
          <select v-model="newCategoryParentId" class="form-select">
            <option :value="null">{{$t('categories.noParent')}}</option>
            <option v-for="cat in hierarchicalCategories" :key="cat.id" :value="cat.id">
              {{ '—'.repeat(cat._level) }} {{ cat.name }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <input type="checkbox" v-model="newCategorySelectable" id="newCategorySelectable" />
          <label for="newCategorySelectable">{{$t('categories.selectable')}}</label>
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">{{$t('categories.create')}}</button>
        </div>
      </div>
    </form>
    <category-tree
      :categories="treeCategories"
      @update="onTreeUpdate"
      :editCategoryId="editCategoryId"
      :editCategoryName="editCategoryName"
      :editCategoryParentId="editCategoryParentId"
      :editCategorySelectable="editCategorySelectable"
      @startEditCategory="startEditCategory"
      @saveEditCategory="saveEditCategory"
      @cancelEdit="cancelEdit"
      @deleteCategory="deleteCategory"
      :getCategoryName="getCategoryName"
      :t="$t"
      :hierarchicalCategories="hierarchicalCategories"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';
import draggable from 'vuedraggable';

const CategoryTree = {
  name: 'CategoryTree',
  components: { draggable },
  props: [
    'categories', 'editCategoryId', 'editCategoryName', 'editCategoryParentId', 'editCategorySelectable',
    'getCategoryName', 't', 'hierarchicalCategories'
  ],
  emits: ['update', 'startEditCategory', 'saveEditCategory', 'cancelEdit', 'deleteCategory'],
  data() {
    return {
      localCategories: JSON.parse(JSON.stringify(this.categories)), // deep copy for drag
      localEditCategoryName: '',
      localEditCategoryParentId: null,
      localEditCategorySelectable: true,
    };
  },
  watch: {
    categories: {
      handler(newVal) {
        this.localCategories = JSON.parse(JSON.stringify(newVal));
      },
      deep: true,
      immediate: true,
    },
    editCategoryId(newVal) {
      if (newVal !== null) {
        const cat = this.categories.find(c => c.id === newVal);
        if (cat) {
          this.localEditCategoryName = cat.name;
          this.localEditCategoryParentId = cat.parent_id === undefined ? null : cat.parent_id;
          this.localEditCategorySelectable = cat.selectable !== undefined ? cat.selectable : true;
        }
      }
    },
  },
  methods: {
    onDragEnd() {
      // Always emit the full tree from the root
      if (!this.$parent || this.$parent.$options.name !== 'CategoryTree') {
        // Root: emit the full tree
        this.$emit('update', this.localCategories);
      } else {
        // Child: propagate up the full tree from the root
        let parent = this.$parent;
        while (parent && parent.$options.name === 'CategoryTree') {
          parent = parent.$parent;
        }
        if (parent) {
          parent.$emit('update', parent.localCategories);
        }
      }
    },
    onChildUpdated(newTree) {
      // Always propagate up to the root
      if (!this.$parent || this.$parent.$options.name !== 'CategoryTree') {
        this.$emit('update', this.localCategories);
      } else {
        let parent = this.$parent;
        while (parent && parent.$options.name === 'CategoryTree') {
          parent = parent.$parent;
        }
        if (parent) {
          parent.$emit('update', parent.localCategories);
        }
      }
    },
    filteredParentOptions(category) {
      // Defensive: always use an array
      const flat = Array.isArray(this.hierarchicalCategories) ? this.hierarchicalCategories : [];
      const getDescendantIds = (catId) => {
        const ids = [];
        const stack = [catId];
        while (stack.length) {
          const currentId = stack.pop();
          for (const cat of flat) {
            if (cat.parent_id === currentId) {
              ids.push(cat.id);
              stack.push(cat.id);
            }
          }
        }
        return ids;
      };
      const descendantIds = getDescendantIds(category.id);
      return flat.filter(catItem => catItem.id !== category.id && !descendantIds.includes(catItem.id));
    },
    cancelEdit() {
      this.$emit('cancelEdit');
    },
    saveEditCategory(category) {
      this.$emit('saveEditCategory', {
        ...category,
        name: this.localEditCategoryName,
        parent_id: this.localEditCategoryParentId,
        selectable: this.localEditCategorySelectable
      });
    },
  },
  template: `
    <draggable
      v-model="localCategories"
      :group="'categories'"
      item-key="id"
      :fallbackOnBody="true"
      :animation="200"
      @end="onDragEnd"
    >
      <template #item="{ element: category }">
        <li :key="category.id" class="list-group-item d-flex flex-column">
          <div class="d-flex justify-content-between align-items-center">
            <div v-if="editCategoryId === category.id" class="d-flex w-100 align-items-center">
              <input v-model="localEditCategoryName" class="form-control me-2" :placeholder="editCategoryId === category.id ? 'Edit category name' : t('categories.newCategoryName')" />
              <select v-model="localEditCategoryParentId" class="form-select me-2">
                <option :value="null">{{$t('categories.noParent')}}</option>
                <option v-for="cat in filteredParentOptions(category)" :key="cat.id" :value="cat.id">
                  {{ '—'.repeat(cat._level) }} {{ cat.name }}
                </option>
              </select>
              <input type="checkbox" v-model="localEditCategorySelectable" :id="'editCategorySelectable' + category.id" class="me-2" />
              <label :for="'editCategorySelectable' + category.id">{{$t('categories.selectable')}}</label>
              <button @click="saveEditCategory(category)" class="btn btn-success btn-sm me-2">{{$t('common.save')}}</button>
              <button @click="cancelEdit" class="btn btn-secondary btn-sm">{{$t('common.cancel')}}</button>
            </div>
            <div v-else class="d-flex w-100 justify-content-between align-items-center">
              <span>{{ category.name }}<span v-if="category.parent_id"> ({{t('categories.parent')}}: {{ getCategoryName(category.parent_id) }})</span><span v-if="!category.selectable"> [{{t('categories.notSelectable')}}]</span></span>
              <div>
                <button type="button" @click="$emit('startEditCategory', category)" class="btn btn-warning btn-sm me-2">{{t('common.edit')}}</button>
                <button type="button" @click="$emit('deleteCategory', category)" class="btn btn-danger btn-sm">{{t('common.delete')}}</button>
              </div>
            </div>
          </div>
          <ul v-if="category.children && category.children.length" class="list-group mt-2">
            <category-tree
              :categories="category.children"
              @update="onChildUpdated"
              @child-updated="onChildUpdated"
              :editCategoryId="editCategoryId"
              :editCategoryName="editCategoryName"
              :editCategoryParentId="editCategoryParentId"
              :editCategorySelectable="editCategorySelectable"
              @startEditCategory="$emit('startEditCategory', $event)"
              @saveEditCategory="$emit('saveEditCategory', $event)"
              @cancelEdit="$emit('cancelEdit')"
              @deleteCategory="$emit('deleteCategory', $event)"
              :getCategoryName="getCategoryName"
              :t="t"
              :hierarchicalCategories="hierarchicalCategories"
            />
          </ul>
        </li>
      </template>
    </draggable>
  `
};

export default {
  name: 'Categories',
  components: { CategoryTree },
  data() {
    return {
      categories: [],
      newCategoryName: '',
      newCategoryParentId: null,
      newCategorySelectable: true,
      editCategoryId: null,
      editCategoryName: '',
      editCategoryParentId: null,
      editCategorySelectable: true,
      localEditCategoryName: '',
      localEditCategoryParentId: null,
      localEditCategorySelectable: true,
      message: '',
      messageType: '', // 'success' or 'error'
    };
  },
  watch: {
    editCategoryId(newVal) {
      if (newVal !== null) {
        const cat = this.categories.find(c => c.id === newVal);
        if (cat) {
          this.localEditCategoryName = cat.name;
          this.localEditCategoryParentId = cat.parent_id === undefined ? null : cat.parent_id;
          this.localEditCategorySelectable = cat.selectable !== undefined ? cat.selectable : true;
        }
      }
    },
  },
  created() {
    this.fetchCategories();
  },
  computed: {
    hierarchicalCategories() {
      // Build a map of id -> category
      const map = {};
      this.categories.forEach(cat => { map[cat.id] = { ...cat, children: [] }; });
      // Assign children
      Object.values(map).forEach(cat => {
        if (cat.parent_id && map[cat.parent_id]) {
          map[cat.parent_id].children.push(cat);
        }
      });
      // Sort children by order recursively (force numeric sort, fallback to id for stability)
      const sortChildren = (cats) => {
        cats.sort((a, b) => {
          const ao = Number(a.order ?? 0);
          const bo = Number(b.order ?? 0);
          if (ao !== bo) return ao - bo;
          return Number(a.id) - Number(b.id);
        });
        cats.forEach(cat => {
          if (cat.children && cat.children.length) {
            sortChildren(cat.children);
          }
        });
      };
      const roots = Object.values(map).filter(cat => !cat.parent_id);
      sortChildren(roots);
      // Recursive flatten with indentation
      const flatten = (cats, level = 0) => {
        let arr = [];
        for (const cat of cats) {
          arr.push({ ...cat, _level: level });
          if (cat.children && cat.children.length) {
            arr = arr.concat(flatten(cat.children, level + 1));
          }
        }
        return arr;
      };
      return flatten(roots);
    },
    treeCategories() {
      // Build a tree structure for nested drag-and-drop
      const map = {};
      this.categories.forEach(cat => { map[cat.id] = { ...cat, children: [] }; });
      Object.values(map).forEach(cat => {
        if (cat.parent_id && map[cat.parent_id]) {
          map[cat.parent_id].children.push(cat);
        }
      });
      // Sort children by order recursively (force numeric sort, fallback to id for stability)
      const sortChildren = (cats) => {
        cats.sort((a, b) => {
          const ao = Number(a.order ?? 0);
          const bo = Number(b.order ?? 0);
          if (ao !== bo) return ao - bo;
          return Number(a.id) - Number(b.id); // fallback to id for stable sort
        });
        cats.forEach(cat => {
          if (cat.children && cat.children.length) {
            sortChildren(cat.children);
          }
        });
      };
      const roots = Object.values(map).filter(cat => !cat.parent_id);
      sortChildren(roots);
      return roots;
    },
  },
  methods: {
    getCategoryName(id) {
      const cat = this.categories.find(c => c.id === id);
      return cat ? cat.name : '';
    },
    async fetchCategories() {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/categories/`);
        this.categories = response.data;
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    },
    async createCategory() {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/v1/categories/`, {
          name: this.newCategoryName,
          parent_id: this.newCategoryParentId,
          selectable: this.newCategorySelectable
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.categories.push(response.data);
        this.newCategoryName = '';
        this.newCategoryParentId = null;
        this.newCategorySelectable = true;
        this.showMessage(this.$t('categories.created'), 'success');
      } catch (error) {
        this.showMessage(error.response?.data?.detail || 'Error creating category', 'error');
      }
    },
    startEditCategory(category) {
      this.editCategoryId = category.id;
      this.editCategoryName = category.name;
      // Ensure null if no parent and handle missing parent_id
      this.editCategoryParentId = (category.parent_id === undefined || category.parent_id === null) ? null : category.parent_id;
      this.editCategorySelectable = category.selectable !== undefined ? category.selectable : true;
    },
    saveEditCategory(payload) {
      // payload contains id, name, parent_id, selectable
      const { id, name, parent_id, selectable } = payload;
      const cat = this.categories.find(c => c.id === id);
      if (!cat) return;
      axios.put(`${API_BASE_URL}/api/v1/categories/${id}`, {
        name,
        parent_id: parent_id === undefined ? null : parent_id,
        selectable
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      }).then(response => {
        Object.assign(cat, response.data);
        this.editCategoryId = null;
        this.editCategoryName = '';
        this.editCategoryParentId = null;
        this.editCategorySelectable = true;
        this.showMessage(this.$t('categories.updated'), 'success');
      }).catch(error => {
        if (error.response && error.response.status === 401) {
          this.showMessage(this.$t('categories.unauthorized'), 'error');
        } else {
          this.showMessage(error.response?.data?.detail || 'Error updating category', 'error');
        }
      });
    },
    cancelEdit() {
      this.editCategoryId = null;
      this.editCategoryName = '';
      this.editCategoryParentId = null;
      this.editCategorySelectable = true;
    },
    async deleteCategory(category) {
      try {
        await axios.delete(`${API_BASE_URL}/api/v1/categories/${category.id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.categories = this.categories.filter(c => c.id !== category.id);
        this.showMessage(this.$t('categories.deleted'), 'success');
      } catch (error) {
        if (error.response && error.response.status === 401) {
          this.showMessage(this.$t('categories.unauthorized'), 'error');
        } else {
          this.showMessage(error.response?.data?.detail || 'Error deleting category', 'error');
        }
      }
    },
    onTreeUpdate(newTree) {
      // Recursively flatten and update parent_id/order, ensuring no duplicates
      const seen = new Set();
      // Always flatten using the current array order, not .order property
      const flatten = (nodes, parentId = null) => {
        let arr = [];
        nodes.forEach((cat, idx) => {
          if (seen.has(cat.id)) return; // skip duplicates
          seen.add(cat.id);
          arr.push({ id: cat.id, parent_id: parentId, order: idx });
          if (cat.children && cat.children.length) {
            arr = arr.concat(flatten(cat.children, cat.id));
          }
        });
        return arr;
      };
      const flat = flatten(newTree);
      // Update local categories
      this.categories.forEach(cat => {
        const found = flat.find(f => f.id === cat.id);
        if (found) {
          cat.parent_id = found.parent_id;
          cat.order = found.order;
        }
      });
      // Send to backend: always send all categories, not just changed ones
      this.updateCategoryOrder(flat);
    },
    async updateCategoryOrder(flat) {
      try {
        await axios.post(`${API_BASE_URL}/api/v1/categories/reorder`, flat, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        this.showMessage(this.$t('categories.reordered'), 'success');
        // Optionally, re-fetch categories to ensure UI is in sync with DB
        await this.fetchCategories();
      } catch (error) {
        if (error.response && error.response.status === 401) {
          this.showMessage(this.$t('categories.unauthorized'), 'error');
        } else {
          this.showMessage(error.response?.data?.detail || 'Error reordering categories', 'error');
        }
      }
    },
    showMessage(msg, type) {
      this.message = msg;
      this.messageType = type;
      setTimeout(() => {
        this.message = '';
        this.messageType = '';
      }, 4000);
    },
  },
};
</script>

<style scoped>
.list-group-item {
  position: relative;
}
</style>