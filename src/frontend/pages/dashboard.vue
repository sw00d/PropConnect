<template>
 <Dashboard />
</template>

<script setup>
import { useDisplay } from 'vuetify'
import Dashboard from "../sections/portal/dashboard/Dashboard"

definePageMeta({
  middleware: ["auth"],
  // TODO SAM FOR SOME REASON AUTHED USERS CANT VIEW DASHBOARD
  // layout: 'protected'
})

const display = ref(useDisplay())


</script>

<style lang="scss" scoped>
.v-data-table-footer {
  display: none !important;
}
</style>
