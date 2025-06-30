<template>
  <div style="text-align:center;">
    <b>🕒</b><br />
    <div v-if="widget.config && widget.config.style === 'circle'" :style="getClockStyle()">
      <div v-for="n in 12" :key="'h'+n" :style="getTickStyle(n*30, true)"></div>
      <div v-for="n in 60" :key="'m'+n" v-if="n%5!==0" :style="getTickStyle(n*6, false)"></div>
      <div :style="getHandStyle(40, 5, ((hour)*30 + minute*0.5), '#222', 2)"></div>
      <div :style="getHandStyle(54, 3, (minute*6 + second*0.1), '#444', 3)"></div>
      <div :style="getHandStyle(58, 2, (second*6), 'red', 4)"></div>
      <div style="position:absolute;left:50%;top:50%;width:14px;height:14px;background:#333;border:2px solid #fff;border-radius:50%;transform:translate(-50%,-50%);z-index:10"></div>
    </div>
    <div v-else style="font-size:2em;">
      {{ timeStr }}
    </div>
  </div>
</template>

<script>
export default {
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
  }
}
</script>
