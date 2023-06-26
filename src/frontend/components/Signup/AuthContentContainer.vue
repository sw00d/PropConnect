<template>
  <div class="wrapper fade-in d-flex align-center">
    <v-container class="mini">
      <v-card>
        <div class="d-flex flex-column px-10 mt-4">
          <div class="d-flex w-100">
            <NuxtLink to="/">
              <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
            </NuxtLink>
          </div>
        </div>
        <div class="d-flex align-center">
          <v-card-text class="w-50 px-10">
            <slot/>
          </v-card-text>
          <v-sheet class="hidden-sm-and-down" width="50%" min-height="434px">
            <v-img :src="image"/>
          </v-sheet>
        </div>

      </v-card>
    </v-container>
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
