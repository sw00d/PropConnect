<template>
  <div class="wrapper">
    <v-container class="py-10">
      <div class="d-flex align-start">
        <div>
          <div class="d-flex align-center mb-4">
            <v-sheet class="d-flex align-center mr-4 bg-transparent">
              <v-img :src="logoGraphic" width="40px"/>
            </v-sheet>
            <v-toolbar-title class="lh-38 text-primary font-weight-black d-flex">
              PropConnect
            </v-toolbar-title>
          </div>
          <div class="opacity-5">
            Using AI to craft simple solutions to <br>
            complex problems.
          </div>
        </div>
        <v-spacer class=""></v-spacer>
        <nuxt-link to="/sign-in">
          <button
            class="border-b sign-in font-14 text-primary"
          >
            Sign in
          </button>
        </nuxt-link>
      </div>

      <div class="d-flex justify-space-between mt-10 font-14">
        <div class="opacity-5">
          © 2023, CKCollab.
        </div>
        <nuxt-link to="/privacy-policy">
          <div class="text-underline text-primary">
            Privacy Policy
          </div>
        </nuxt-link>

      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
// Imports
import logoGraphic from "~/assets/logos/logo-graphic-only.png"

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.wrapper {
  background: linear-gradient(40deg, #cae0ee, #fcfcfc 50%, #cae0ee);
}

.sign-in {
  height: 18px;
  border-color: var(--v-theme-primary) !important;
}

</style>
