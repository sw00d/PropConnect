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
                        <v-sheet width="200px" v-if="activeConversationType === 'assistant'"
                                 class="font-12 ml-3 bg-transparent">
                            *The initial conversation with the AI
                        </v-sheet>
                        <v-sheet width="200px" v-else class="font-12 ml-3 bg-transparent">
                            *The conversation between the vendor and the tenant
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
                        class="border pa-3 rounded-lg mt-4 overflow-auto bg-surface"
                        max-height="80vh"
                        ref="conversationContainerRef"
                    >
                        <div
                            v-for="(message,i) in activeConversationMessages"
                            :key="i"
                            class="d-flex flex-column"
                        >
                            <div v-if="message.role === 'user' && message.sender_number === tenant?.number"
                                 class="left-msg">
                                <div class="font-12 text-highContrast">
                                    {{
                                        conversation.tenant?.name || `Tenant ${$formatPhoneNumber(conversation.tenant.number)}`
                                    }}
                                </div>
                                <div class="rounded-lg pa-2 bg-surfaceSecondary">
                                    <MessageContent :message="message"/>
                                </div>
                            </div>

                            <div v-else-if="vendor?.number === message.sender_number" class="right-msg">
                                <div class="font-12 text-highContrast text-right">
                                    {{
                                        conversation.vendor?.name || `Vendor ${$formatPhoneNumber(conversation.vendor.number)}`
                                    }}
                                </div>
                                <div class="rounded-lg pa-2 bg-primary">
                                    <MessageContent :message="message"/>
                                </div>
                            </div>

                            <div v-else-if="message.role === 'assistant'" class="right-msg mt-3">
                                <div class="font-12 text-highContrast text-right">
                                    {{
                                        activeConversationType === 'assistant' ? 'AI Assistant' : conversation.vendor?.name
                                    }}
                                </div>
                                <div class="rounded-lg pa-2 bg-primary">
                                    <MessageContent :message="message"/>
                                </div>
                            </div>

                            <div v-else-if="message.role === 'admin' || message.role === 'admin_to_tenant'"
                                 class="right-msg mt-3">
                                <div class="font-12 text-highContrast text-right">
                                    Property Manager
                                </div>
                                <div class="rounded-lg pa-2 bg-blue">
                                    <MessageContent :message="message"/>
                                </div>
                            </div>

                        </div>
                    </v-sheet>


                    <div class="mt-3 text-right">* Refresh to load new messages</div>

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
                                :disabled="!convoIsActive"
                            />
                            <!--            TODO Disable this if the convo isn't active aka 3 days old I think? -->
                            <v-btn
                                width="100px"
                                height="50px"
                                color="primary"
                                :loading="sendingMessage"
                                @click="sendMessage"
                                :disabled="!convoIsActive || !message?.length"
                            >
                                Send
                            </v-btn>
                        </div>
                        <v-alert
                            v-if="!conversation.point_of_contact_has_interjected && activeConversationType === 'assistant'"
                            color="primary"
                            border="start"
                            variant="tonal"
                            class="text-warning d-flex weight-700 mt-3"
                        >
                            {{
                                activeConversationType === 'assistant' && 'If you interject here, we will bypass all AI responses for the remainder of the conversation.'
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
import {useRequest} from "../../../composables/useRequest"
import {onMounted, ref, nextTick} from 'vue'
import dayjs from "dayjs"
import MessageContent from "../../../components/MessageContent"
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

const convoIsActive = computed(() => {
    return conversation.value.is_active || activeConversationToggle.value === 0
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
    }
)

</script>

<style scoped lang="stylus">
.table-row {
    min-height: 48px;
    display flex
    justify-content space-between
    align-items center
}

.left-msg {
    align-self: start;
    max-width: 66%;
}

.right-msg {
    align-self: end;
    max-width: 66%;

}
</style>
