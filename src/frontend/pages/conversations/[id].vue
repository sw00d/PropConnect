<template>
  <v-container>
    <div class="d-md-flex text-left flex-column justify-center align-center">
      <v-row class="fill-width">
        <v-col>
          <ConversationDetail/>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup>
import ConversationDetail from "../../sections/portal/conversations/ConversationDetail"

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
