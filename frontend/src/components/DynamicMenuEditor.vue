<template>
  <div class="menu-editor-full">
    <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger']" role="alert">
      {{ message }}
    </div>
    <h3 class="mb-4">Menu Editor</h3>
    <ul class="list-group">
      <draggable :list="menu" group="menu" :move="onMove" item-key="id" :clone="cloneMenuItem" @change="emitUpdate">
        <template #item="{element, index}">
          <li class="list-group-item d-flex flex-column">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center w-100">
                <span class="drag-handle me-2">☰</span>
                <div class="d-flex flex-wrap flex-grow-1">
                  <input v-for="lang in languages" :key="lang" v-model="element.label[lang]" :placeholder="'Label ('+lang+')'" class="form-control me-2 mb-1" style="max-width: 160px;" />
                  <input v-model="element.route" placeholder="Route (e.g. /items)" class="form-control me-2 mb-1" style="max-width: 180px;" />
                  <select v-model="element.visibility" class="form-select me-2 mb-1" style="width:120px">
                    <option value="public">Public</option>
                    <option value="registered">Registered</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <button class="btn btn-danger btn-sm me-2" @click="removeMenuItem(index)">Delete</button>
                <button class="btn btn-secondary btn-sm" @click="addSubMenu(element)" :disabled="level >= 3">Add Submenu</button>
              </div>
            </div>
            <ul v-if="element.children && element.children.length > 0" class="list-group mt-2">
              <dynamic-menu-editor
                :menu="element.children"
                :languages="languages"
                :level="level+1"
                @update="emitUpdate"
              />
            </ul>
          </li>
        </template>
      </draggable>
    </ul>
    <button class="btn btn-primary mt-3" @click="addMenuItem">Add Menu Item</button>
  </div>
</template>

<script>
import draggable from 'vuedraggable';
export default {
  name: 'DynamicMenuEditor',
  components: { draggable, DynamicMenuEditor: undefined },
  props: {
    menu: { type: Array, required: true },
    languages: { type: Array, required: true },
    level: { type: Number, default: 1 },
  },
  emits: ['update'],
  data() {
    return {
      message: '',
      messageType: '',
    };
  },
  mounted() {
    this.$options.components.DynamicMenuEditor = this.$options;
  },
  methods: {
    addMenuItem() {
      const newItem = {
        id: Date.now() + Math.random(),
        label: Object.fromEntries(this.languages.map(l => [l, ''])),
        route: '',
        visibility: 'public',
        children: this.level < 3 ? [] : undefined,
      };
      this.menu.push(newItem);
      this.emitUpdate();
      this.showMessage('Menu item added', 'success');
    },
    addSubMenu(item) {
      if (!item.children && this.level < 3) this.$set(item, 'children', []);
      if (item.children && this.level < 3) {
        item.children.push({
          id: Date.now() + Math.random(),
          label: Object.fromEntries(this.languages.map(l => [l, ''])),
          route: '',
          visibility: 'public',
          children: this.level < 3 ? [] : undefined,
        });
        this.emitUpdate();
        this.showMessage('Submenu added', 'success');
      }
    },
    removeMenuItem(index) {
      this.menu.splice(index, 1);
      this.emitUpdate();
      this.showMessage('Menu item deleted', 'success');
    },
    onMove(e) {
      return (e.relatedContext.component.level <= 3);
    },
    cloneMenuItem(item) {
      return JSON.parse(JSON.stringify(item));
    },
    emitUpdate() {
      this.$emit('update', this.menu);
    },
    showMessage(msg, type) {
      this.message = msg;
      this.messageType = type;
      setTimeout(() => {
        this.message = '';
        this.messageType = '';
      }, 2000);
    }
  },
  watch: {
    menu: {
      handler() { this.emitUpdate(); },
      deep: true
    },
    languages(newLangs) {
      const fillLangs = (items) => {
        items.forEach(item => {
          newLangs.forEach(l => { if (!item.label[l]) item.label[l] = ''; });
          if (item.children) fillLangs(item.children);
        });
      };
      fillLangs(this.menu);
    }
  }
}
</script>

<style scoped>
.menu-editor-full {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 0 24px 0;
  background: #fff;
}
.list-group-item {
  position: relative;
}
.drag-handle {
  cursor: grab;
  margin-right: 8px;
  font-size: 1.2em;
}
</style>
