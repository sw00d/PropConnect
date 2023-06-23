<template>
  <HomeHero/>
  <ProductIntro1 />
  <ProductIntro2 />
</template>

<script setup>

import HomeHero from "../sections/homepage/HomeHero"
import ProductIntro1 from "../sections/homepage/ProductIntro1"
import ProductIntro2 from "../sections/homepage/ProductIntro2"

definePageMeta({
  layout: "public",
  middleware: ["guest"]
})

</script>
