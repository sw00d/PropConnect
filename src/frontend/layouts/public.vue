<template>
  <v-layout class="flex-column">
    <v-main>
      <div>
        <slot/>
        <Footer/>
      </div>
    </v-main>
  </v-layout>

</template>

<script setup lang="ts">
import {useAuth} from "~/composables/useAuth";
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";
import Footer from "~/sections/homepage/Footer.vue";

const auth = useAuth()

useThemeSwitcher()

</script>

<style lang="stylus" scoped>
</style>
