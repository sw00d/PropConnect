<template>
  <div class="">
    <div class="content-container d-flex justify-space-between align-center py-16">
      <v-row>
        <v-col cols="4" class="d-flex align-center">
          <v-sheet height="300px" width="360px" class="bg-transparent">
            <v-img :src="textingGirl"/>
          </v-sheet>
        </v-col>
        <v-col class="pl-10 relative">
          <v-sheet class="absolute bottom right bg-transparent" width="470px" height="350px">
            <v-img :src="blueblob"/>
          </v-sheet>
          <div class="d-flex flex-column justify-center h-100">
            <div class="font-weight-bold font-40 lh-50">
              <div>
                AI Capabilities
              </div>
              <div class="ml-14 pl-16">
                Everyday Tech
              </div>
            </div>
            <div class="font-weight-medium opacity-7 font-24 mt-11">
              We leverage familiar texting for seamless communication, connecting tenants and vendors effortlessly. Skip
              the hassle of new accounts and passwords. With our accessible help line, tenants can text anytime, and our
              AI will link them to the ideal vendor for their needs.
            </div>
          </div>
        </v-col>

      </v-row>
    </div>

  </div>
</template>

<script setup lang="ts">
import textingGirl from "assets/public-site/textingGirl.png"
import blueblob from "assets/public-site/blueblob.png"
// Imports

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
