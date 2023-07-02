<template>
  <div class="wrapper">
    <v-container class="py-10">
      <div class="d-flex align-start">
        <div>

          <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
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
        <div class="text-underline text-primary">
          Privacy Policy
        </div>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
// Imports

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
