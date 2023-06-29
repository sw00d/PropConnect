<template>
 <ConversationHome />
</template>

<script setup>
import { useDisplay } from 'vuetify'
import ConversationHome from "../sections/portal/conversations/home/ConversationHome"

definePageMeta({
  middleware: ["auth"],
  layout: 'protected'
})

const display = ref(useDisplay())


</script>

<style lang="scss" scoped>
.v-data-table-footer {
  display: none !important;
}
</style>
