<template>
  <v-layout class="flex-column">
    <v-main>
      <div>
        <slot/>
      </div>
    </v-main>
  </v-layout>

</template>

<script setup lang="ts">
import {useAuth} from "~/composables/useAuth";

const auth = useAuth()


</script>

<style lang="stylus" scoped>
</style>
