<template>
  <div>
    <div class="d-flex justify-space-between">
      <div class="font-60 font-weight-bold lh-70">
        Meet Your New AI <br/>
        Maintenance Coordinator
      </div>
      <v-sheet width="250px">
        <v-img
          :src="robotSVG"
        />
      </v-sheet>
    </div>

    <div class="d-flex justify-space-between align-center mt-10">
      <div class="font-30 opacity-5 font-weight-bold ls-0 mr-10">
        Harness the power of AI to streamline tenant issue resolution, connecting problems to solutions with seamless
        precision.
      </div>

      <v-btn
        variant="flat"
        width="250px"
        height="50px"
        class="font-weight-black bg-primary font-20"
      >
        Get Started
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports
import robotSVG from "@/assets/robotSVG.svg"

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
