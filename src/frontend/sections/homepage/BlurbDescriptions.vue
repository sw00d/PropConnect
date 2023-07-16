<template>
  <v-container class="d-flex flex-column relative">

    <v-sheet class="absolute left opacity-1 mt-16 bg-transparent" width="680" height="600" max-width="100%">
      <v-img :src="orangeblob"/>
    </v-sheet>

    <div class="font-weight-black font-40 lh-50 my-16 text-center text-md-left">
      How it Works
    </div>

    <v-sheet class="blurb one bg-primary">
      <div class="font-30 font-weight-bold">
        1) AI-Powered Tenant Hotline
      </div>
      <div class="font-20 mt-6">
        Grant your tenants access to a unique, AI-powered hotline, facilitating fast and hassle-free reporting of their
        maintenance issues. This direct line of communication simplifies the process, enabling efficient issue
        reporting.
      </div>
    </v-sheet>

    <v-sheet class="blurb two bg-secondary my-16 align-self-end text-right">
      <div class="font-30 font-weight-bold">
        2) Intelligent Vendor Detection
      </div>
      <div class="font-20 mt-6">
        Rely on our advanced AI to understand and analyze maintenance requests. It automatically pinpoints the issue and
        identifies the most suitable vendor from your network.
      </div>
    </v-sheet>

    <v-sheet class="blurb three bg-primary">
      <div class="font-30 font-weight-bold">
        3) Streamlined Vendor Communication
      </div>
      <div class="font-20 mt-6">
        Our platform sets up a secure and transparent communication channel between the tenant and the vendor. This
        streamlines real-time updates, photo sharing, and convenient scheduling.
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
