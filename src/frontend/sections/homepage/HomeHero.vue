<template>
  <div class="wrapper">
    <div class="d-flex flex-column py-5">
      <div class="d-flex justify-center w-100">
        <div class="content-container d-flex align-center">
          <v-toolbar-title class="font-30 lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
          <v-spacer></v-spacer>
          <button
            class="border-b sign-in font-14 text-primary"
            @click="logout"
          >
            Sign in
          </button>
        </div>
      </div>
    </div>

    <div class="mt-10 content-container">
      <div class="d-flex justify-space-between align-center">
        <div class="font-60 font-weight-black lh-70">
          Meet Your New AI <br/>
          Maintenance Coordinator
        </div>
        <v-sheet width="250px" height="250px" class="bg-transparent">
          <v-img
            transition="slide-x-reverse-transition"
            :src="robotSVG"
          />
        </v-sheet>
      </div>

      <div class="d-flex justify-space-between align-center mt-5">
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
  </div>
</template>

<script setup lang="ts">
// Imports
import robotSVG from "assets/public-site/robotSVG.svg"

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.wrapper {
  min-height 100vh
  background: radial-gradient(circle, #fcfcfc, #cae0ee);
}
</style>
