<template>
  <v-container class="d-flex justify-space-between align-center py-16">
    <v-row>
      <v-col sm="12" md="6" class="d-flex align-center justify-center justify-md-space-between">
        <v-sheet height="300px" width="360px" class="bg-transparent">
          <v-img :src="textingGirl" transition="slide-x-transition"/>
        </v-sheet>
      </v-col>
      <v-col class="pl-md-0 relative d-flex justify-center justify-md-start">
        <v-sheet class="absolute bottom right bg-transparent" width="470px" height="350px">
          <v-img :src="blueblob"/>
        </v-sheet>
        <v-sheet
          class="d-flex flex-column justify-center h-100 bg-transparent align-center align-sm-start"
          :max-width="isTablet ? '100%' : '80%'"
        >
          <div class="font-weight-black font-40 lh-50">
            <div>
              AI Capabilities
            </div>
            <div class="ml-md-14 pl-sm-16 text-no-wrap">
              Everyday Tech
            </div>
          </div>
          <div class="font-weight-medium opacity-7 text-h6 mt-11">
            We leverage familiar texting for seamless communication, connecting tenants and vendors effortlessly. Skip
            the hassle of new accounts and passwords. With our accessible help line, tenants can text anytime, and our
            AI will link them to the ideal vendor for their needs.
          </div>
        </v-sheet>
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import textingGirl from "assets/public-site/textingGirl.png"
import blueblob from "assets/public-site/blueblob.png"
import {useDisplay} from "vuetify";
// Imports

// Data
const breakpoint = useDisplay()
const isTablet = computed(() => breakpoint.smAndUp)
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
