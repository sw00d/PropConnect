<template>
  <div class="wrapper">
    <div class="d-flex flex-column">
      <div class="d-flex justify-center w-100">
        <v-container class="d-flex align-center">
          <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
          <v-spacer class="hidden-sm-and-down"></v-spacer>
          <nuxt-link :to="store?.isLoggedIn ? '/dashboard' : '/sign-in'">
            <button
              class="border-b sign-in font-14 text-primary"
            >
              {{ store?.isLoggedIn ? 'Portal' : 'Sign in' }}
            </button>
          </nuxt-link>
        </v-container>
      </div>
    </div>

    <v-container class="mt-sm-10">
      <div class="d-flex justify-space-between align-center">
        <div class="text-h3 text-sm-h2 font-weight-black lh-70">
          Meet Your New AI <br/>
          Maintenance Coordinator
        </div>
        <v-sheet width="250px" height="250px" class="bg-transparent hidden-xs">
          <v-img
            transition="slide-x-reverse-transition"
            :src="robotSVG"
          />
        </v-sheet>
      </div>

      <div class="d-flex justify-space-between flex-column flex-md-row mt-5">
        <div class="text-h6 opacity-5 ls-0 mr-10">
          Harness the power of <i><b>AI</b></i> to streamline tenant issue resolution, effortlessly connecting problems
          with the <i><b>right solutions</b></i>.
        </div>

        <v-btn
          variant="flat"
          width="250px"
          height="50px"
          class="font-weight-black bg-primary font-20 mt-10"
          to="/signup/user-info"
        >
          Get Started
        </v-btn>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
// Imports
import robotSVG from "assets/public-site/robotSVG.svg"
import {useUserStore} from "~/store/userStore";

// Data
const store = useUserStore()
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.wrapper {
  padding-bottom: 100px
  background: radial-gradient(circle, #fcfcfc, #cae0ee);
}

.sign-in {
  height: 18px;
  border-color: var(--v-theme-primary) !important;
}
</style>
