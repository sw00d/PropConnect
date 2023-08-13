<template>
    <v-container>
        <div class="d-md-flex text-left flex-column justify-center align-center">
            <ConversationDetail/>
        </div>
    </v-container>
</template>

<script setup>
import ConversationDetail from "../../sections/portal/conversations/conversation-detail/ConversationDetail.vue"

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
