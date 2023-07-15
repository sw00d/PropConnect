<template>
 <ConversationHome />
</template>

<script setup>
import ConversationHome from "../../sections/portal/conversations/home/ConversationHome"

definePageMeta({
  middleware: ["auth"],
  layout: 'protected'
})


</script>

<style lang="scss" scoped>
.v-data-table-footer {
  display: none !important;
}
</style>
