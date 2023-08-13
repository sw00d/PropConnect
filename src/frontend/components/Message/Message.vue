<template>
    <div v-if="message" class="d-flex flex-column">
        <!-- User Message -->
        <div v-if="isUserMessage" class="left-msg">
            <div class="font-12 text-highContrast">{{ displayName }}</div>
            <div class="rounded-lg pa-2 bg-surfaceSecondary">
                <MessageContent :message="message"/>
            </div>
        </div>

        <!-- Vendor Message -->
        <div v-else-if="isVendorMessage" class="right-msg">
            <div class="font-12 text-highContrast text-right">{{ vendorName }}</div>
            <div class="rounded-lg pa-2 bg-primary">
                <MessageContent :message="message"/>
            </div>
        </div>

        <!-- Assistant Message -->
        <div v-else-if="isAssistantMessage" class="right-msg mt-3">
            <div class="font-12 text-highContrast text-right">{{ assistantName }}</div>
            <div class="rounded-lg pa-2 bg-primary">
                <MessageContent :message="message"/>
            </div>
        </div>

        <!-- Admin Message -->
        <div v-else-if="isAdminMessage" class="w-100 my-4">
            <div class="d-flex justify-space-between font-12">
                <div class="text-highContrast">Property Manager</div>
                <div>
                    <v-icon color="green" size="14">mdi-check</v-icon>
                    Sent to both parties
                </div>
            </div>
            <div class="rounded-lg pa-2 bg-blue">
                <MessageContent :message="message"/>
            </div>
        </div>
        
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
    message: Object,
    tenant: Object,
    vendor: Object,
    activeConversationType: String,
})
const { $formatPhoneNumber } = useNuxtApp()

// Computed properties
const isUserMessage = computed(() => {
    return props.message.role === 'user' && props.message.sender_number === props.tenant?.number
})

const isVendorMessage = computed(() => {
    return props.vendor?.number === props.message.sender_number
})

const isAssistantMessage = computed(() => {
    return props.message.role === 'assistant'
})

const isAdminMessage = computed(() => {
    return props.message.role === 'admin' || props.message.role === 'admin_to_tenant'
})

const displayName = computed(() => {
    return props.tenant?.name || `Tenant ${ $formatPhoneNumber(props.tenant.number) }`
})

const vendorName = computed(() => {
    return props.vendor?.name || `Vendor ${ $formatPhoneNumber(props.vendor.number) }`
})

const assistantName = computed(() => {
    return props.activeConversationType === 'assistant' ? 'AI Assistant' : props.vendor?.name
})
</script>

<style scoped lang="stylus">

.left-msg {
    align-self: start;
    max-width: 66%;
}

.right-msg {
    align-self: end;
    max-width: 66%;
}
</style>
