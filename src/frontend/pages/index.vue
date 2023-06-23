<template>
  <HomeHero/>
</template>

<script setup>

import HomeHero from "../sections/homepage/HomeHero"

definePageMeta({
  layout: "public",
  middleware: ["guest"]
})

</script>
