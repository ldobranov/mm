<template>
  <header class="bg-dark text-white text-center p-3">
    <h1>{{ siteName }}</h1>
  </header>
</template>

<script>
export default {
  name: "Header",
  props: {
    siteName: {
      type: String,
      required: true
    }
  }
};
</script>

<style scoped>
header {
  letter-spacing: 1px;
  font-size: 1.5rem;
}
</style>
