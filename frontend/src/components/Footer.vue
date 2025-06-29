<template>
  <footer class="bg-dark text-white text-center p-3 mt-4">
    <p>&copy; {{ year }} {{ siteName }}</p>
  </footer>
</template>

<script>
export default {
  name: "Footer",
  props: {
    siteName: {
      type: String,
      required: true
    }
  },
  computed: {
    year() {
      return new Date().getFullYear();
    }
  }
};
</script>

<style scoped>
footer {
  font-size: 1rem;
}
</style>
