<template>
  <div style="min-width:220px;max-width:100%;margin:auto;">
    <b>⛏️ HiveOS {{ mode === 'farm' ? 'Farm' : 'Rig' }}</b>
    <div v-if="mode === 'farm'">
      <div v-if="!token || !farmId" style="margin-top:10px;">
        <div class="mb-2"><input v-model="token" placeholder="API Token" class="form-control form-control-sm" /></div>
        <div class="mb-2"><input v-model="farmId" placeholder="Farm ID" class="form-control form-control-sm" /></div>
        <button class="btn btn-sm btn-primary" @click="saveConfig(); fetchFarm()">Connect</button>
      </div>
      <div v-else>
        <button class="btn btn-sm btn-secondary me-1" @click="fetchFarm">Refresh</button>
        <button class="btn btn-sm btn-success me-1" @click="sendFarmAction('start')">Start All</button>
        <button class="btn btn-sm btn-danger me-1" @click="sendFarmAction('stop')">Stop All</button>
        <div v-if="loading" class="mt-2">Loading...</div>
        <div v-if="error" class="text-danger mt-2">{{ error }}</div>
        <div
          v-if="farm && farm.rigs && farm.rigs.length"
          class="rigs-grid"
        >
          <div
            v-for="rig in farm.rigs"
            :key="rig.worker_id"
            class="rig-box"
            :style="{ background: rigStatusColor(rig), color: '#222', border: '1px solid #bbb' }"
            @click="openRigPopup(rig)"
            style="cursor:pointer;"
          >
            <b>{{ rig.name }}</b>
            <div style="font-size:0.8em;">
              <div>Uptime: {{ rig.stats && rig.stats.boot_time ? formatUptime(rig.stats.boot_time) : '-' }}</div>
              <div v-if="rig.gpu_stats && rig.gpu_stats.length">Temp: {{ rig.gpu_stats[0].temp }}°C</div>
              <div v-if="rig.miners_summary && rig.miners_summary.hashrates && rig.miners_summary.hashrates.length">
                Hashrate: {{ (rig.miners_summary.hashrates[0].hash/1000).toFixed(2) }} MH/s
              </div>
            </div>
          </div>
        </div>
        <!-- Rig Action Popup -->
        <div v-if="showRigPopup" class="rig-popup-backdrop" @click.self="closeRigPopup">
          <div class="rig-popup">
            <h5>{{ selectedRig?.name }}</h5>
            <div style="font-size:0.9em;">
              <div>Uptime: {{ selectedRig && selectedRig.stats && selectedRig.stats.boot_time ? formatUptime(selectedRig.stats.boot_time) : '-' }}</div>
              <div v-if="selectedRig && selectedRig.gpu_stats && selectedRig.gpu_stats.length">Temp: {{ selectedRig.gpu_stats[0].temp }}°C</div>
              <div v-if="selectedRig && selectedRig.miners_summary && selectedRig.miners_summary.hashrates && selectedRig.miners_summary.hashrates.length">
                Hashrate: {{ (selectedRig.miners_summary.hashrates[0].hash/1000).toFixed(2) }} MH/s
              </div>
            </div>
            <div class="mt-3 d-flex flex-wrap gap-2 justify-content-center">
              <button class="btn btn-sm btn-success" @click="rigAction('miners/start')">Start Miner</button>
              <button class="btn btn-sm btn-warning" @click="rigAction('miners/stop')">Stop Miner</button>
              <button class="btn btn-sm btn-info" @click="rigAction('reboot')">Reboot Miner</button>
              <button class="btn btn-sm btn-danger" @click="rigAction('shutdown')">Shutdown</button>
              <button class="btn btn-sm btn-secondary" @click="closeRigPopup">Close</button>
            </div>
            <div v-if="popupLoading" class="mt-2">Loading...</div>
            <div v-if="popupError" class="text-danger mt-2">{{ popupError }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <div v-if="!token || !farmId || !workerId" style="margin-top:10px;">
        <div class="mb-2"><input v-model="token" placeholder="API Token" class="form-control form-control-sm" /></div>
        <div class="mb-2"><input v-model="farmId" placeholder="Farm ID" class="form-control form-control-sm" /></div>
        <div class="mb-2"><input v-model="workerId" placeholder="Worker ID" class="form-control form-control-sm" /></div>
        <button class="btn btn-sm btn-primary" @click="saveConfig(); fetchRig()">Connect</button>
      </div>
      <div v-else>
        <button class="btn btn-sm btn-secondary me-1" @click="fetchRig">Refresh</button>
        <button class="btn btn-sm btn-success me-1" @click="sendRigAction('start')">Start Miner</button>
        <button class="btn btn-sm btn-warning me-1" @click="sendRigAction('stop')">Stop Miner</button>
        <button class="btn btn-sm btn-info me-1" @click="sendRigAction('reboot')">Reboot Miner</button>
        <button class="btn btn-sm btn-danger" @click="sendRigAction('shutdown')">Shutdown</button>
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
  </div>
</template>

<script>
import axios from 'axios'
export default {
  props: {
    widget: Object,
    mode: {
      type: String,
      default: 'rig' // or 'farm'
    }
  },
  data() {
    return {
      loading: false,
      error: '',
      rig: null,
      farm: null,
      token: '',
      farmId: '',
      workerId: '',
      showRigPopup: false,
      selectedRig: null,
      popupLoading: false,
      popupError: '',
    }
  },
  watch: {
    // Watch for config changes and sync to widget.config
    token(val) {
      this.saveConfig();
    },
    farmId(val) {
      this.saveConfig();
    },
    workerId(val) {
      if (this.mode !== 'farm') this.saveConfig();
    },
    mode(val) {
      // If mode changes, clear workerId if farm mode
      if (val === 'farm') this.workerId = '';
      this.saveConfig();
    }
  },
  async mounted() {
    if (this.widget.config) {
      this.token = this.widget.config.token || '';
      this.farmId = this.widget.config.farmId || '';
      this.workerId = this.widget.config.workerId || '';
      // Support mode from config if present
      if (this.widget.config.mode) this.$emit('update:mode', this.widget.config.mode);
    }
    if (this.mode === 'farm') {
      if (this.token && this.farmId) await this.fetchFarm();
    } else {
      if (this.token && this.farmId && this.workerId) await this.fetchRig();
    }
  },
  methods: {
    async fetchFarm() {
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.post('/api/v1/hiveos/farm', {
          token: this.token,
          farm_id: this.farmId
        });
        this.farm = res.data;
      } catch (e) {
        this.error = e.response?.data?.detail || e.message || 'Error fetching farm';
      } finally {
        this.loading = false;
      }
    },
    async fetchRig() {
      this.loading = true;
      this.error = '';
      try {
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
    async sendFarmAction(action) {
      this.loading = true;
      this.error = '';
      // Only allow valid actions for farm
      let apiAction = null;
      if (action === 'start' || action === 'miners/start') apiAction = 'miners/start';
      else if (action === 'stop' || action === 'miners/stop') apiAction = 'miners/stop';
      else if (action === 'reboot') apiAction = 'reboot';
      else if (action === 'shutdown') apiAction = 'shutdown';
      else {
        this.error = `Unsupported farm action: ${action}`;
        this.loading = false;
        return;
      }
      const payload = {
        token: this.token,
        farm_id: this.farmId,
        action: apiAction
      };
      console.log('[HiveWidget] Sending farm action:', apiAction, 'Payload:', payload);
      try {
        await axios.post('/api/v1/hiveos/farm/action', payload)
          .then(res => {
            console.log('[HiveWidget] Farm action response:', res);
            if (res.data && res.data.results) {
              // Log all results
              res.data.results.forEach(r => {
                if (r.status === 'ok') {
                  console.log(`[HiveWidget] Farm action success for worker ${r.worker_id}`);
                } else {
                  console.error(`[HiveWidget] Farm action failed for worker ${r.worker_id}: ${r.error}`);
                }
              });
              // Show summary error if any failures
              const failed = res.data.results.filter(r => r.status !== 'ok');
              if (failed.length > 0) {
                this.error = `Failed for ${failed.length} rig(s): ` + failed.map(f => `${f.worker_id || '?'} (${f.error})`).join(', ');
              }
            } else if (res.data && res.data.error) {
              this.error = res.data.error;
            }
          });
        await this.fetchFarm();
      } catch (e) {
        console.error('[HiveWidget] Farm action error:', e);
        this.error = e.response?.data?.detail || e.message || 'Error sending farm action';
      } finally {
        this.loading = false;
      }
    },
    async sendRigAction(action) {
      this.loading = true;
      this.error = '';
      const payload = {
        token: this.token,
        farm_id: this.farmId,
        worker_id: this.workerId,
        action: action
      };
      console.log('[HiveWidget] Sending rig action:', action, 'Payload:', payload);
      try {
        const res = await axios.post('/api/v1/hiveos/rig/action', payload);
        console.log('[HiveWidget] Rig action response:', res);
        await this.fetchRig();
      } catch (e) {
        console.error('[HiveWidget] Rig action error:', e);
        this.error = e.response?.data?.detail || e.message || 'Error sending rig action';
      } finally {
        this.loading = false;
      }
    },
    saveConfig() {
      // Save all relevant config fields
      this.widget.config.token = this.token;
      this.widget.config.farmId = this.farmId;
      if (this.mode !== 'farm') {
        this.widget.config.workerId = this.workerId;
      } else {
        delete this.widget.config.workerId;
      }
      this.widget.config.mode = this.mode;
    },
    formatUptime(bootTime) {
      const now = Math.floor(Date.now() / 1000);
      const diff = now - bootTime;
      const h = Math.floor(diff / 3600);
      const m = Math.floor((diff % 3600) / 60);
      return h + 'h ' + m + 'm';
    },
    rigStatusColor(rig) {
      if (rig.stats?.online === true) return '#b6fcb6'; // green
      if (rig.stats?.online === false) return '#ffb6b6'; // red
      return '#ffe7b6'; // orange/unknown
    },
    openRigPopup(rig) {
      this.selectedRig = rig;
      this.showRigPopup = true;
      this.popupError = '';
    },
    closeRigPopup() {
      this.showRigPopup = false;
      this.selectedRig = null;
      this.popupError = '';
    },
    async rigAction(action) {
      // Defensive: try to get worker_id from all possible places
      let workerId = null;
      if (this.selectedRig && this.selectedRig.worker_id) {
        workerId = this.selectedRig.worker_id;
      } else if (this.selectedRig && this.selectedRig.id) {
        workerId = this.selectedRig.id;
      } else if (typeof this.selectedRig === 'string' || typeof this.selectedRig === 'number') {
        workerId = this.selectedRig;
      }
      if (!workerId) {
        this.popupError = 'worker_id missing for this rig!';
        return;
      }
      this.popupLoading = true;
      this.popupError = '';
      // Only allow valid actions for rig
      let apiAction = null;
      if (action === 'start' || action === 'miners/start') apiAction = 'miners/start';
      else if (action === 'stop' || action === 'miners/stop') apiAction = 'miners/stop';
      else if (action === 'reboot') apiAction = 'reboot';
      else if (action === 'shutdown') apiAction = 'shutdown';
      else {
        this.popupError = `Unsupported rig action: ${action}`;
        this.popupLoading = false;
        return;
      }
      // Compose payload and remove undefined/null fields
      const payload = {
        token: this.token,
        farm_id: this.farmId,
        worker_id: String(workerId),
        action: apiAction
      };
      Object.keys(payload).forEach(
        k => (payload[k] === undefined || payload[k] === null) && delete payload[k]
      );
      console.log('[HiveWidget] Sending rig popup action:', apiAction, 'Payload:', payload);
      try {
        const res = await axios.post('/api/v1/hiveos/rig/action', payload);
        console.log('[HiveWidget] Rig popup action response:', res);
        if (res.data && res.data.error) {
          this.popupError = res.data.error;
          return;
        }
        // Optionally check for backend error in response body
        if (res.data && res.data.error) {
          this.popupError = res.data.error;
        } else {
          await this.fetchFarm();
          this.closeRigPopup();
        }
      } catch (e) {
        console.error('[HiveWidget] Rig popup action error:', e);
        // Show backend error message if available
        if (e.response?.data?.detail) {
          this.popupError = e.response.data.detail;
        } else if (e.response?.data?.message) {
          this.popupError = e.response.data.message;
        } else if (e.response?.data?.error) {
          this.popupError = e.response.data.error;
        } else if (e.response?.status === 400) {
          this.popupError = 'Bad request: check action and worker_id. Try "miners/restart" for restart.';
        } else {
          this.popupError = e.message || 'Error sending action';
        }
      } finally {
        this.popupLoading = false;
      }
    },
  }
}
</script>

<style scoped>
.rigs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 8px;
  justify-items: stretch;
  align-items: stretch;
  margin-top: 8px;
  max-width: 100%;
}
.rig-box {
  aspect-ratio: 1 / 1;
  width: 100%;
  min-width: 90px;
  max-width: 100%;
  padding: 6px 4px;
  border-radius: 8px;
  font-size: 0.85em;
  box-sizing: border-box;
  word-break: break-word;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}
.rig-popup-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
}
.rig-popup {
  background: #fff;
  border-radius: 10px;
  padding: 24px 20px 16px 20px;
  min-width: 220px;
  min-height: 120px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.18);
  max-width: 90vw;
  max-height: 90vh;
  text-align: center;
}
</style>

<!-- This file is correct and up to date for your HiveWidget component. -->
<!-- If you do not see your changes on the display page, make sure: -->

<!-- 1. The Display page is importing and using this file as the HiveWidget component. -->
<!-- 2. There are no duplicate or old HiveWidget.vue files elsewhere in your project. -->
<!-- 3. Your build is up to date (restart Vite/dev server after changes). -->
<!-- 4. In Display.vue, the widget rendering code should look like: -->
<!-- <component -->
<!--   :is="getWidgetComponent(widget)" -->
<!--   :widget="widget" -->
<!--   v-bind="widget.type === 'hive' ? { mode: widget.config?.mode || 'rig' } : {}" -->
<!-- /> -->

<!-- 5. In Display.vue, getWidgetComponent(widget) should return this HiveWidget.vue for type 'hive'. -->

<!-- If you still see old code (e.g. status text, one column), search your project for other HiveWidget.vue files or for the string "Status:" and remove/replace them. -->
<!-- Also, clear your browser cache and do a full reload after rebuilding. -->
