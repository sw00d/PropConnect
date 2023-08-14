<template>
    <div class="pb-10 w-100">
        <v-btn
            @click="navigateTo('/conversations')"
        >
            <v-icon>mdi-chevron-left</v-icon>
            Back
        </v-btn>
        <v-sheet class="d-flex align-center justify-center bg-transparent" height="70vh" v-if="loading">
            <v-progress-circular
                size="64"
                indeterminate
                color="primary"
            />
        </v-sheet>
        <div v-else>
            <VendorAssignCard
                v-if="!conversation.vendor"
                :conversation="conversation"
                @refreshConversation="fetchConversation"
            />
            <v-row class="fade-in mt-10">
                <v-col md="6" xs="12" sm="12" class="bg">
                    <v-card>
                        <v-card-title class="font-weight-bold">
                            Conversation Details
                        </v-card-title>

                        <v-card-text>

                            <div class="table-row border-b">
                                <div class="weight-700 font-16">
                                    Date started:
                                </div>
                                <div>

                                    {{ dayjs(conversation.date_created).format('MMM D, YYYY - H:mma') }}
                                </div>
                            </div>

                            <div class="table-row border-b">
                                <div class="weight-700 font-16">
                                    Tenant:
                                </div>
                                <div>
                                    {{ conversation.tenant?.name || "No Name" }}: {{
                                        $formatPhoneNumber(conversation.tenant.number)
                                    }}
                                </div>
                            </div>

                            <div class="table-row border-b">
                                <div class="weight-700 font-16">
                                    Address:
                                </div>
                                <div>
                                    {{ conversation.tenant?.address || "No address" }}
                                </div>
                            </div>

                            <div class="table-row border-b">
                                <div class="weight-700 font-16">
                                    Vendor:
                                </div>
                                <div v-if="conversation.vendor?.number">
                                    {{ conversation.vendor?.name || "No Name" }}: {{
                                        $formatPhoneNumber(conversation.vendor?.number)
                                    }}
                                </div>
                                <div v-else>
                                    No Vendor Assigned
                                </div>
                            </div>

                            <div class="table-row border-b">
                                <div class="weight-700 font-16">
                                    Status:
                                </div>
                                <v-btn-toggle
                                    v-model="activeConversationToggle"
                                    density="compact"
                                    class="d-flex align-center"
                                >
                                    <v-btn
                                        color="success"
                                        height="20px"
                                        :loading="updatingActiveStatus && activeConversationToggle === 0"
                                        :class="{ 'no-pointer-events': activeConversationToggle === 0 }"
                                        size="small"
                                        @click="toggleActiveStatus"
                                    >
                                        <template #loader>
                                            <v-progress-circular size="14" indeterminate color="white" width="2"/>
                                        </template>
                                        Active
                                    </v-btn>

                                    <v-btn
                                        color="error"
                                        height="20px"
                                        :loading="updatingActiveStatus && activeConversationToggle === 1"
                                        :class="{ 'no-pointer-events': activeConversationToggle === 1 }"
                                        size="small"
                                        @click="toggleActiveStatus"
                                    >
                                        <template #loader>
                                            <v-progress-circular size="14" indeterminate color="white" width="2"/>
                                        </template>
                                        Inactive
                                    </v-btn>
                                </v-btn-toggle>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>

                <v-col md="6" sm="12">
                    <div>
                        <div class="d-flex align-center">
                            <v-chip
                                class="mr-3"
                                @click="switchConversationView('assistant')"
                                :variant="activeConversationType === 'vendor' ? 'outlined' : 'flat'"
                            >
                                Assistant
                            </v-chip>
                            <v-chip
                                :disabled="!conversation.vendor?.number"
                                @click="switchConversationView('vendor')"
                                :variant="activeConversationType === 'assistant' ? 'outlined' : 'flat'"
                            >
                                Vendor
                            </v-chip>
                        </div>
                        <v-sheet
                            class="font-12 bg-transparent ml-1 mt-2"
                        >
                            {{
                                activeConversationType === 'assistant' ? 'The initial conversation with the AI' : 'The conversation between the vendor and the tenant'
                            }}
                        </v-sheet>
                    </div>
                    <div
                        v-if="conversation.vendor?.number === conversation.tenant.number && activeConversationType === 'vendor'"
                        class="text-warning mt-3 font-12"
                    >
                        <v-icon>mdi-alert</v-icon>
                        Tenant and vendor numbers are the same, so this conversation history may not be accurate
                    </div>
                    <v-sheet
                        class="border pa-3 rounded-lg mt-2 overflow-auto bg-surface"
                        max-height="80vh"
                        ref="conversationContainerRef"
                    >
                        <v-row class="d-flex" v-if="activeConversationType === 'vendor'">
                            <v-col>
                                <div class="font-12 text-highContrast">
                                    Initial Message to Tenant
                                </div>
                                <pre class="bg-grey font-14 rounded-lg pa-2 text-pre-line">{{ conversation.tenant_intro_message }}</pre>
                            </v-col>
                            <v-col>
                                <div class="font-12 text-highContrast">
                                    Initial Message to Vendor
                                </div>
                                <pre class="bg-grey font-14 rounded-lg pa-2 text-pre-line">{{ conversation.vendor_intro_message }}</pre>
                            </v-col>
                        </v-row>
                        <div
                            v-for="(message,i) in activeConversationMessages"
                            :key="i"
                            class="d-flex flex-column"
                        >
                            <Message
                                :message="message"
                                :tenant="tenant"
                                :vendor="vendor"
                                :activeConversationType="activeConversationType"
                            />
                        </div>
                    </v-sheet>


                    <div class="mt-3 text-right font-12">* Refresh to load new messages</div>

                    <div class="mt-2">
                        <div class="font-12 opacity-8 mb-1">Property manager:</div>
                        <div class="d-flex align-center">
                            <v-textarea
                                v-model="message"
                                variant="outlined"
                                placeholder="Type a message..."
                                hide-details
                                class="mr-2"
                                auto-grow
                                rows="1"
                                :disabled="disabledCustomMessage"
                            />
                            <!--            TODO Disable this if the convo isn't active aka 3 days old I think? -->
                            <v-btn
                                width="100px"
                                height="50px"
                                color="primary"
                                :loading="sendingMessage"
                                @click="sendMessage"
                                :disabled="disabledCustomMessage && !message?.length"
                            >
                                Send
                            </v-btn>
                        </div>
                        <v-alert
                            v-if="activeConversationType === 'assistant' && !conversation.vendor"
                            color="primary"
                            border="start"
                            variant="tonal"
                            class="text-warning d-flex weight-700 mt-3"
                        >
                            {{
                                activeConversationType === 'assistant' &&
                                'If you interject here, we will bypass all AI responses for the remainder of the conversation.'
                            }}
                        </v-alert>

                    </div>

                </v-col>
            </v-row>
        </div>
    </div>

</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {useRequest} from "../../../../composables/useRequest"
import {onMounted, ref, nextTick} from 'vue'
import dayjs from "dayjs"
import Message from "../../../../components/Message/Message.vue"
import {useSnackbarStore} from "~/store/snackbarStore";
import VendorAssignCard from "~/sections/portal/conversations/conversation-detail/VendorAssignCard.vue";

const {$formatPhoneNumber} = useNuxtApp()

const route = useRoute()
const {id} = route.params
const snackbarStore = useSnackbarStore()

const conversation = ref({})
const conversationContainerRef = ref(null)
const vendor = computed(() => conversation.value?.vendor)
const tenant = computed(() => conversation.value?.tenant)

const loading = ref(true)

const updatingActiveStatus = ref(false)
const activeConversationToggle = ref(3)

const sendingMessage = ref(false)
const activeConversationType = ref<"assistant" | "vendor">('assistant')
const message = ref('')

const activeConversationMessages = computed(() => {
    if (activeConversationType.value === 'assistant') {
        return conversation.value.assistant_messages
    } else {
        return conversation.value.vendor_messages
    }
})

const disabledCustomMessage = computed(() => {
    return !conversation.value.is_active || (activeConversationType.value === 'assistant' && conversation.value.vendor)
})

const fetchConversation = async () => {
    try {
        const {data, execute} = useRequest(`/conversations/${id}`)
        await execute()
        conversation.value = data.value
        activeConversationToggle.value = conversation.value.is_active ? 0 : 1
        activeConversationType.value = conversation.value.vendor_messages?.length ? 'vendor' : 'assistant'
    } catch (error) {
        console.error(error)
        // alert('Error fetching conversation')
        // errors.value = error.value.data
        snackbarStore.displaySnackbar('error', 'Error fetching details')

    } finally {
        setTimeout(() => loading.value = false, 1000)
    }
}

const setLastViewed = async () => {
    const {execute} = useRequest(`/conversations/${id}/set_last_viewed/`, {method: 'POST'})
    await execute()
}

const toggleActiveStatus = async () => {
    try {
        updatingActiveStatus.value = true
        const {error} = await useRequest(`/conversations/${id}/`, {
            method: 'PATCH',
            body: {
                is_active: !conversation.value.is_active
            }
        })
        if (error.value) {
            throw new Error(error)
        }
    } catch (error) {
        console.error(error)
        activeConversationToggle.value = conversation.value.is_active ? 0 : 1
        alert('Error updating. Contact support.')
    } finally {
        updatingActiveStatus.value = false
    }
}


const sendMessage = async () => {
    sendingMessage.value = true
    try {
        const url = activeConversationType.value === 'assistant' ? `conversations/${id}/send_admin_message_to_tenant/` : `conversations/${id}/send_admin_message_to_group/`
        const res = await useRequest(url, {
            method: 'POST',
            body: {
                message_body: `[PROPERTY MANAGER]: ${message.value}`,
            },
        })
        if (res.error?.value) {
            throw new Error(res.error.value)
        }
        await fetchConversation()
        await nextTick()
        conversationContainerRef.value.scrollTop = conversationContainerRef.value.scrollHeight
    } catch (e) {
        console.error(e)
        snackbarStore.displaySnackbar('error', 'Error fetching details')
    } finally {
        message.value = ''
        sendingMessage.value = false
    }
}


const switchConversationView = (view) => {
    activeConversationType.value = view
}

onMounted(() => {
    fetchConversation()
    setLastViewed()
})

onUnmounted(() => {
    setLastViewed()
})

</script>

<style scoped lang="stylus">
.table-row {
    min-height: 48px;
    display flex
    justify-content space-between
    align-items center
}

</style>
