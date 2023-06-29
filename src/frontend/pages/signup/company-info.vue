<template>
  <CompanyInformation />
</template>

<script setup lang="ts">
// Imports

import CompanyInformation from "~/sections/company-signup/CompanyInformation.vue";

definePageMeta({
  middleware: ["auth"],
  layout: "signup",
})

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
