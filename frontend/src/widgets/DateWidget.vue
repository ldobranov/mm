<template>
  <div style="font-size:1.5em;text-align:center;">
    <b>📅</b><br>{{ dateStr }}
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
    dateStr() {
      const fmt = this.widget.config?.format || 'YYYY-MM-DD';
      if (fmt === 'YYYY-MM-DD') {
        return this.now.getFullYear() + '-' + String(this.now.getMonth()+1).padStart(2,'0') + '-' + String(this.now.getDate()).padStart(2,'0');
      }
      if (fmt === 'DD.MM.YYYY') {
        return String(this.now.getDate()).padStart(2,'0') + '.' + String(this.now.getMonth()+1).padStart(2,'0') + '.' + this.now.getFullYear();
      }
      return this.now.toLocaleDateString();
    }
  }
}
</script>
