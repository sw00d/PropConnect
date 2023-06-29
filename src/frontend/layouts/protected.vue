<template>
  <v-card>
    <v-layout>
      <v-navigation-drawer
        theme="light"
        permanent
      >
        <v-list-item>
          <NuxtLink to="/dashboard">
            <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
          </NuxtLink>
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

          <NuxtLink to="/conversations">
            <v-list-item
                            class="my-3"

              prepend-icon="mdi-forum"
              title="Conversations"
              value="conversations"
            ></v-list-item>
          </NuxtLink>
          <v-list-item prepend-icon="mdi-account-hard-hat" title="Vendors" value="vendors"></v-list-item>
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
      <v-main style="min-height: 100vh"></v-main>
    </v-layout>
  </v-card>

</template>

<script setup lang="ts">
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";
import {useUserStore} from "~/store/userStore";
import {useRoute} from "vue-router";

const route = useRoute()
const user = useUserStore()
useThemeSwitcher()

</script>

<style lang="stylus" scoped>
.v-main
  background: url("assets/grid_light.svg") 0 0 repeat;

</style>
