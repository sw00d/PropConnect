<template>
  <v-layout class="flex-column">
    <v-main>
      <div>
        <!--        <v-btn-->
        <!--          icon-->
        <!--          variant="outlined"-->
        <!--          class="transition z-index-1"-->
        <!--          @click="toggle_theme"-->
        <!--        >-->
        <!--          <v-icon-->
        <!--            :class="theme.global.current.value.dark ? 'rotate-180 icon' : ' icon'"-->
        <!--            icon="mdi-theme-light-dark"-->
        <!--            size="30px"-->
        <!--          />-->
        <!--        </v-btn>-->
        <slot/>
      </div>
    </v-main>
  </v-layout>

</template>

<script setup lang="ts">
import {useAuth} from "~/composables/useAuth";
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";

const auth = useAuth()

const {theme, toggle_theme} = useThemeSwitcher()

</script>

<style lang="stylus" scoped>
</style>
