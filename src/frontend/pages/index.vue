<template>
  <div class="fade-in">
    <HomeHero/>
    <ProductIntro1/>
    <ProductIntro2/>
    <BlurbDescriptions/>
    <ReadyToJumpIn/>
  </div>
</template>

<script setup>

import HomeHero from "../sections/homepage/HomeHero"
import ProductIntro1 from "../sections/homepage/ProductIntro1"
import ProductIntro2 from "../sections/homepage/ProductIntro2"
import BlurbDescriptions from "../sections/homepage/BlurbDescriptions"
import ReadyToJumpIn from "../sections/homepage/ReadyToJumpIn"

definePageMeta({
  layout: "public",
  // middleware: ["guest"]
})

</script>
