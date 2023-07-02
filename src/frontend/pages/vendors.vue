<template>
  <VendorList />
</template>

<script setup>
import VendorList from "../sections/portal/vendors/VendorList"

definePageMeta({
  middleware: ["auth"],
  layout: 'protected'
})

</script>

<style lang="scss" scoped>
</style>
