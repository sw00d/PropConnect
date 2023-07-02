<template>
  <div>
    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title class="d-flex align-center">
        <span class="lh-38 text-primary font-20 font-weight-black ">
          PropConnect
        </span>
         <v-chip color="success" class="font-weight-bold absolute top right mt-1 mr-1" variant="flat" size="small">
          ✨ Beta
        </v-chip>
      </v-toolbar-title>
    </v-app-bar>

    <PortalNavigationDrawer v-model="drawer" isMobile/>

  </div>
</template>

<script setup lang="ts">
// Imports

// Data
import {useRoute} from "vue-router";
import {useUserStore} from "~/store/userStore";
import PortalNavigationDrawer from "~/components/Layout/PortalNavigationDrawer.vue";

const user = useUserStore()
const drawer = ref(false)
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
