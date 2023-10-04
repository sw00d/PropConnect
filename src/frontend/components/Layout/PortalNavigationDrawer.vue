<template>
  <v-navigation-drawer
    theme="light"
    :permanent="!isMobile"
  >
    <v-list-item v-if="!props.isMobile">
      <div class="d-flex justify-space-between  align-center">
        <NuxtLink to="/dashboard">
          <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
        </NuxtLink>
        <v-chip color="success" class="font-weight-bold absolute top right mt-1 mr-1" variant="flat" size="small">
          ✨ Beta
        </v-chip>
      </div>
    </v-list-item>
    <v-list
      nav
    >
      <NuxtLink to="/dashboard">
        <v-list-item
          class="my-3"
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          value="dashboard"
          :active="route.path === '/dashboard'"
        ></v-list-item>
      </NuxtLink>

      <NuxtLink to="#">
        <v-list-item
          class="my-3"
          prepend-icon="mdi-forum"
          title="Conversations"
          value="conversations"
          :active="route.path === '/conversations'"

        ></v-list-item>
      </NuxtLink>

      <NuxtLink to="/vendors">
        <v-list-item
          class="my-3"
          prepend-icon="mdi-account-hard-hat"
          title="Vendors"
          value="vendors"
          :active="route.path === '/vendors'"
        >
        </v-list-item>
      </NuxtLink>

       <NuxtLink to="/settings">
        <v-list-item
          class="my-3"
          prepend-icon="mdi-cog"
          title="Settings"
          value="settings"
          :active="route.path === '/settings'"
        >
        </v-list-item>
      </NuxtLink>

    </v-list>

    <template v-slot:append>
      <div class="pa-2">
        <v-btn rounded="0" size="small" @click="user.logout()" class="justify-start">
          Sign out
          <v-icon class="ml-1">mdi-logout</v-icon>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
// Imports

// Data
import {useRoute} from "vue-router";
import {useUserStore} from "~/store/userStore";

const route = useRoute()
const user = useUserStore()

const props = defineProps({
  isMobile: {
    type: Boolean,
    required: true
  }
})
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
