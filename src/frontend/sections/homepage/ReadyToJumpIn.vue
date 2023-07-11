<template>
  <div class="bg-secondary mt-16">
    <v-container>
      <div class="d-flex justify-center justify-md-space-between">
        <div class="d-flex flex-column align-center text-center align-md-start text-md-left">
          <div class="font-40 font-weight-black text-no-wrap">
            Ready to jump in?
          </div>
          <div class="text-h6 mt-5">
            <span class="opacity-5">
              Signing up takes 2 minutes! Let's start the journey together.
            </span>
            😃
          </div>
          <v-sheet height="250px" class="bg-transparent my-10 hidden-md-and-up">
            <v-img :src="pool"/>
          </v-sheet>

          <v-btn
            variant="flat"
            class="font-weight-black bg-primary font-20 mt-10"
            width="288px"
            height="60px"
            to="/signup/user-info"
          >
            Start my journey
          </v-btn>
          <div class="opacity-5 mt-2">Starting at $12/month</div>
        </div>

        <v-sheet height="250px" class="bg-transparent d-md-flex hidden-sm-and-down">
          <v-img :src="pool"/>
        </v-sheet>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
// Imports
import pool from "@/assets/public-site/pool.png"

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.v-container {
  padding-top 100px !important
  padding-bottom 100px !important
}
</style>
