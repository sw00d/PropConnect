<template>
  <v-container class="d-flex flex-column relative">

    <v-sheet class="absolute left opacity-1 mt-16 bg-transparent" width="680" height="600">
      <v-img :src="orangeblob"/>
    </v-sheet>

    <v-sheet class="blurb one bg-primary">
      <div class="font-30 font-weight-bold">
        Automated Tenant Issue Analysis
      </div>
      <div class="font-20 mt-6">
        Experience the efficiency of AI as it interprets and categorizes tenant issues, matches an appropriate vendor,
        and
        saves you precious time and effort.
      </div>
    </v-sheet>

    <v-sheet class="blurb two bg-secondary my-16 align-self-end text-right">
      <div class="font-30 font-weight-bold">
        Automated Tenant Issue Analysis
      </div>
      <div class="font-20 mt-6">
        Experience the efficiency of AI as it interprets and categorizes tenant issues, matches an appropriate vendor,
        and
        saves you precious time and effort.
      </div>
    </v-sheet>

    <v-sheet class="blurb three bg-primary">
      <div class="font-30 font-weight-bold">
        Automated Tenant Issue Analysis
      </div>
      <div class="font-20 mt-6">
        Experience the efficiency of AI as it interprets and categorizes tenant issues, matches an appropriate vendor,
        and
        saves you precious time and effort.
      </div>
    </v-sheet>
  </v-container>
</template>

<script setup lang="ts">
import orangeblob from "@/assets/public-site/orangeblob.png"
// Imports

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.blurb {
  padding 20px 20px
  border-radius 18px
  position relative
  width: 90%;
}

.blurb.three::after, .blurb.one::after {
  content: '';
  position absolute;
  left 0;
  bottom: -30px;
  border-top: 30px solid transparent
  border-bottom: 30px solid transparent
  border-left: 30px solid #000080;
}

.blurb.two::after {
  content: '';
  position absolute;
  right 0;
  bottom: -30px;
  border-top: 30px solid transparent;
  border-bottom: 30px solid transparent;
  border-right: 30px solid #8CD1FD;
  background transparent;
}

@media (min-width: 960px) {
  .blurb {
    padding 30px 60px
    width: 56%;
  }
}


</style>
