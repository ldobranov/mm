<template>
  <div :style="{ minHeight: '100vh', background: background }">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Display</h2>
      <input type="color" v-model="background" title="Change background color" />
    </div>
    <draggable
      v-model="widgets"
      class="widget-canvas"
      :options="{ animation: 200, handle: '.widget-handle' }"
      item-key="id"
    >
      <template #item="{ element: widget }">
        <div
          :key="widget.id"
          class="widget-box resizable"
          :style="widgetStyle(widget)"
          @mousedown.stop
          @mousedown.right.prevent="startResize($event, widget)"
        >
          <div class="widget-handle">☰</div>
          <component
            :is="getWidgetComponent(widget)"
            :widget="widget"
            v-bind="widget.type === 'hive' ? { mode: widget.config?.mode || 'rig' } : {}"
          />
          <div class="resize-corner" @mousedown.stop.prevent="startResize($event, widget)"></div>
        </div>
      </template>
    </draggable>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { defineAsyncComponent } from 'vue'

// Dummy widget components for now
const ClockWidget = {
  props: ['widget'],
  data() {
    return {
      now: new Date(),
      timer: null
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.now = new Date();
    }, 1000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
  computed: {
    timeStr() {
      return this.now.toLocaleTimeString();
    },
    hour() {
      return this.now.getHours() % 12;
    },
    minute() {
      return this.now.getMinutes();
    },
    second() {
      return this.now.getSeconds();
    }
  },
  methods: {
    getClockStyle() {
      return {
        width: '120px',
        height: '120px',
        border: '6px solid #333',
        borderRadius: '50%',
        position: 'relative',
        margin: '0 auto',
        background: 'radial-gradient(circle, #fff 80%, #e0e0e0 100%)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
      };
    },
    getHandStyle(length, width, angle, color, z = 1) {
      return {
        position: 'absolute',
        left: '50%',
        top: '50%',
        width: width + 'px',
        height: length + 'px',
        background: color,
        transform: 'translate(-50%, -100%) rotate(' + angle + 'deg)',
        transformOrigin: 'bottom center',
        borderRadius: '2px',
        zIndex: z,
        boxShadow: color === 'red' ? '0 0 4px #f00' : '',
      };
    },
    getTickStyle(angle, big) {
      return {
        position: 'absolute',
        left: '50%',
        top: '50%',
        width: big ? '4px' : '2px',
        height: big ? '16px' : '8px',
        background: big ? '#333' : '#bbb',
        transform: 'translate(-50%, -100%) rotate(' + angle + 'deg)',
        transformOrigin: 'bottom center',
        borderRadius: '2px',
        zIndex: 0,
      };
    }
  },
  template: `
    <div style="text-align:center;">
      <b>🕒</b><br />
      <div v-if="widget.config && widget.config.style === 'circle'" :style="getClockStyle()">
        <div v-for="n in 12" :key="'h'+n" :style="getTickStyle(n*30, true)"></div>
        <div v-for="m in 60" :key="'m'+m" v-if="m%5!==0" :style="getTickStyle(m*6, false)"></div>
        <div :style="getHandStyle(40, 5, ((hour)*30 + minute*0.5), '#222', 2)"></div>
        <div :style="getHandStyle(54, 3, (minute*6 + second*0.1), '#444', 3)"></div>
        <div :style="getHandStyle(58, 2, (second*6), 'red', 4)"></div>
        <div style="position:absolute;left:50%;top:50%;width:14px;height:14px;background:#333;border:2px solid #fff;border-radius:50%;transform:translate(-50%,-50%);z-index:10"></div>
      </div>
      <div v-else style="font-size:2em;">
        {{ timeStr }}
      </div>
    </div>
  `
}
const DateWidget = {
  props: ['widget'],
  data() {
    return {
      now: new Date(),
      timer: null
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.now = new Date();
    }, 1000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
  computed: {
    dateStr() {
      const fmt = this.widget.config?.format || 'YYYY-MM-DD';
      // Simple formatting for common cases
      if (fmt === 'YYYY-MM-DD') {
        return this.now.getFullYear() + '-' + String(this.now.getMonth()+1).padStart(2,'0') + '-' + String(this.now.getDate()).padStart(2,'0');
      }
      if (fmt === 'DD.MM.YYYY') {
        return String(this.now.getDate()).padStart(2,'0') + '.' + String(this.now.getMonth()+1).padStart(2,'0') + '.' + this.now.getFullYear();
      }
      // Fallback to locale
      return this.now.toLocaleDateString();
    }
  },
  template: `<div style="font-size:1.5em;text-align:center;">
    <b>📅</b><br>{{ dateStr }}
  </div>`
}
const TempWidget = {
  props: ['widget'],
  template: `<div><b>Temp</b></div>`
}
const HiveWidget = defineAsyncComponent(() => import('../widgets/HiveWidget.vue'))

export default {
  name: 'Display',
  components: { draggable, HiveWidget },
  data() {
    return {
      widgets: [],
      background: '#f8f9fa',
    }
  },
  async mounted() {
    await this.fetchWidgets()
  },
  watch: {
    widgets: {
      handler() {
        this.saveLayout()
      },
      deep: true
    },
    background: {
      handler() {
        this.saveLayout()
      }
    }
  },
  methods: {
    async fetchWidgets() {
      const res = await axios.get(`${API_BASE_URL}/api/v1/widgets/`)
      let widgets = res.data.filter(w => w.enabled)
      this.widgets = widgets
      // Load background color from the first widget (optional)
      if (widgets.length && widgets[0].background) {
        this.background = widgets[0].background
      }
    },
    async saveLayout() {
      // Save size, pos, and background for each widget to the backend
      for (const w of this.widgets) {
        await axios.put(`${API_BASE_URL}/api/v1/widgets/${w.id}`, {
          ...w,
          size: w.size,
          pos: w.pos,
          background: this.background
        })
      }
    },
    getWidgetComponent(widget) {
      if (widget.type === 'clock') return ClockWidget
      if (widget.type === 'date') return DateWidget
      if (widget.type === 'temp') return TempWidget
      if (widget.type === 'hive') return HiveWidget // <-- ensure this is the imported HiveWidget
      return {
        template: '<div>Unknown widget</div>'
      }
    },
    widgetStyle(widget) {
      return {
        position: 'relative',
        width: widget.size?.w + 'px',
        height: widget.size?.h + 'px',
        margin: '10px',
        display: 'inline-block',
        background: '#fff',
        border: '1px solid #ccc',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
        overflow: 'hidden',
      }
    },
    startResize(e, widget) {
      if (!widget.size) {
        widget.size = { w: 200, h: 100 };
      }
      const startX = e.clientX;
      const startY = e.clientY;
      const startW = widget.size.w;
      const startH = widget.size.h;
      const onMouseMove = (ev) => {
        widget.size.w = Math.max(100, startW + (ev.clientX - startX));
        widget.size.h = Math.max(60, startH + (ev.clientY - startY));
      };
      const onMouseUp = () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        this.saveLayout();
      };
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    },
  }
}
</script>

<style scoped>
.widget-canvas {
  min-height: 80vh;
  padding: 20px;
  background: transparent;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}
.widget-box {
  user-select: none;
  transition: box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  margin: 10px;
  overflow: hidden;
  position: relative;
}
.widget-handle {
  cursor: move;
  background: #eee;
  padding: 2px 8px;
  border-bottom: 1px solid #ccc;
  font-size: 1.1em;
  user-select: none;
}
.resize-corner {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  background: #888;
  opacity: 0.7;
  border-radius: 0 0 8px 0;
  cursor: se-resize;
  z-index: 2;
}
</style>
