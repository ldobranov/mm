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
          <component :is="getWidgetComponent(widget)" :widget="widget" />
          <div class="resize-corner" @mousedown.stop.prevent="startResize($event, widget)"></div>
        </div>
      </template>
    </draggable>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import axios from 'axios'

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
        <!-- Hour marks -->
        <div v-for="n in 12" :key="'h'+n" :style="getTickStyle(n*30, true)"></div>
        <div v-for="n in 60" :key="'m'+n" v-if="n%5!==0" :style="getTickStyle(n*6, false)"></div>
        <!-- Hands -->
        <div :style="getHandStyle(40, 5, ((hour)*30 + minute*0.5), '#222', 2)"></div>
        <div :style="getHandStyle(54, 3, (minute*6 + second*0.1), '#444', 3)"></div>
        <div :style="getHandStyle(58, 2, (second*6), 'red', 4)"></div>
        <!-- Center -->
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
const HiveWidget = {
  props: ['widget'],
  data() {
    return {
      loading: false,
      error: '',
      rig: null,
      token: '',
      farmId: '',
      workerId: '',
    }
  },
  async mounted() {
    if (this.widget.config) {
      this.token = this.widget.config.token || '';
      this.farmId = this.widget.config.farmId || '';
      this.workerId = this.widget.config.workerId || '';
    }
    if (this.token && this.farmId && this.workerId) {
      await this.fetchRig();
    }
  },
  methods: {
    async fetchRig() {
      this.loading = true;
      this.error = '';
      try {
        // Use backend proxy endpoint
        const res = await axios.post('/api/v1/hiveos/rig', {
          token: this.token,
          farm_id: this.farmId,
          worker_id: this.workerId
        });
        this.rig = res.data;
      } catch (e) {
        this.error = e.response?.data?.detail || e.message || 'Error fetching rig';
      } finally {
        this.loading = false;
      }
    },
    async sendAction(action) {
      this.loading = true;
      this.error = '';
      try {
        // Use backend proxy endpoint for actions
        await axios.post('/api/v1/hiveos/rig/action', {
          token: this.token,
          farm_id: this.farmId,
          worker_id: this.workerId,
          action: action
        });
        await this.fetchRig();
      } catch (e) {
        this.error = e.response?.data?.detail || e.message || 'Error sending action';
      } finally {
        this.loading = false;
      }
    },
    saveConfig() {
      this.widget.config.token = this.token;
      this.widget.config.farmId = this.farmId;
      this.widget.config.workerId = this.workerId;
    },
    formatUptime(bootTime) {
      // bootTime is a unix timestamp, current time is now
      const now = Math.floor(Date.now() / 1000);
      const diff = now - bootTime;
      const h = Math.floor(diff / 3600);
      const m = Math.floor((diff % 3600) / 60);
      return h + 'h ' + m + 'm';
    }
  },
  template: `
    <div style="min-width:220px;max-width:350px;margin:auto;">
      <b>⛏️ HiveOS Rig</b>
      <div v-if="!token || !farmId || !workerId" style="margin-top:10px;">
        <div class="mb-2"><input v-model="token" placeholder="API Token" class="form-control form-control-sm" /></div>
        <div class="mb-2"><input v-model="farmId" placeholder="Farm ID" class="form-control form-control-sm" /></div>
        <div class="mb-2"><input v-model="workerId" placeholder="Worker ID" class="form-control form-control-sm" /></div>
        <button class="btn btn-sm btn-primary" @click="saveConfig(); fetchRig()">Connect</button>
      </div>
      <div v-else>
        <button class="btn btn-sm btn-secondary me-1" @click="fetchRig">Refresh</button>
        <button class="btn btn-sm btn-success me-1" @click="sendAction('miners/start')">Start Miner</button>
        <button class="btn btn-sm btn-warning me-1" @click="sendAction('miners/stop')">Stop Miner</button>
        <button class="btn btn-sm btn-danger" @click="sendAction('shutdown')">Shutdown</button>
        <div v-if="loading" class="mt-2">Loading...</div>
        <div v-if="error" class="text-danger mt-2">{{ error }}</div>
        <div v-if="rig" class="mt-2" style="font-size:0.95em;">
          <div><b>Name:</b> {{ rig.name }}</div>
          <div><b>Status:</b> {{ rig.stats?.online ? 'Online' : 'Offline' }}</div>
          <div><b>Uptime:</b> {{ rig.stats && rig.stats.boot_time ? formatUptime(rig.stats.boot_time) : '-' }}</div>
          <div><b>Temp:</b> <span v-if="rig.gpu_stats && rig.gpu_stats.length">{{ rig.gpu_stats[0].temp }}°C</span></div>
          <div><b>Hashrate:</b> <span v-if="rig.miners_summary && rig.miners_summary.hashrates && rig.miners_summary.hashrates.length">{{ (rig.miners_summary.hashrates[0].hash/1000).toFixed(2) }} MH/s</span></div>
        </div>
      </div>
    </div>
  `
}

export default {
  name: 'Display',
  components: { draggable },
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
      const res = await axios.get('/api/v1/widgets/')
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
        await axios.put(`/api/v1/widgets/${w.id}`, {
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
      if (widget.type === 'hive') return HiveWidget
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
