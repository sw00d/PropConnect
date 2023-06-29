<template>
  <div class="wrapper fade-in d-flex align-center fade-in">
    <v-card-text class="px-10">
      <slot/>
    </v-card-text>
  </div>
</template>

<script setup lang="ts">
// Imports

// Data
const props = defineProps({
  image: {
    type: Object,
    required: true
  }
})

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.wrapper {
  min-height: 100vh;
  min-width: 100vw;
  background: url("assets/grid_light.svg") 0 0 repeat;
}
</style>
