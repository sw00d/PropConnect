<template>
    <v-alert
        color="primary"
        border="start"
        variant="tonal"
        class="mt-3"
    >
        <div class="d-flex flex-column flex-md-row">
            <div class="mr-md-4 mb-4 mb-md-0 d-flex align-start">
                <v-sheet>
                    <v-icon color="warning" class="mr-2 mt-1">mdi-alert-circle</v-icon>
                </v-sheet>
                <div>
                    <div class="font-weight-bold font-20">
                        Vendor Assignment Needed
                    </div>
                    <div>
                        Once assigned, we will start a conversation between the tenant and the vendor.
                    </div>
                </div>
            </div>
            <v-sheet min-width="30%" class="d-flex flex-1 align-center my-2">
                <div class="flex-1">
                    <v-select
                        :menu-props="{ closeOnContentClick: true }"
                        :items="vendors"
                        hide-details
                        v-model="selectedVendor"
                        class="mr-4"
                        label="Vendor"
                        ref="selectRef"

                    >
                        <template #selection="{ item }">
                            <div class="font-16">
                                {{ item.value.name }}
                            </div>
                        </template>
                        <template #item="{ item }">
                            <v-list-item
                                class="d-flex"
                                :class="{'no-pointer-events': !item.value.has_opted_in}"
                                @click="selectVendor(item)"
                            >
                                {{ item.value.name }}
                                <v-chip
                                    v-if="!item.value.has_opted_in"
                                    color="warning"
                                    class="ml-5 weight-600"
                                >
                                    Must Opt in
                                </v-chip>
                            </v-list-item>
                        </template>
                    </v-select>
                </div>
                <v-btn
                    color="primary"
                    class="white--text"
                    @click="assignVendor"
                    :loading="assigning"
                    :disabled="!selectedVendor?.id"
                >
                    Assign
                </v-btn>
            </v-sheet>
        </div>

        <hr class="my-4">

        <div class="font-20 font-weight-bold">
            Customize Intro Messages
            <v-btn
                color="white"
                class="ml-2"
                height="30px"
                width="30px"
                icon
                @click="editIntroMessages = !editIntroMessages"
            >
                <v-icon v-if="!editIntroMessages">mdi-chevron-right</v-icon>
                <v-icon v-else>mdi-chevron-down</v-icon>
            </v-btn>
        </div>
        <v-slide-y-transition>
            <div v-if="editIntroMessages">
                <div class="mb-6 mt-5 font-14 opacity-8">
                    Craft the first message that will be sent to the tenant and vendor in this conversation.
                    Include any details for the vendor that you feel is relevant.
                </div>
                <v-row>
                    <v-col cols="12" md="6">
                        <v-textarea
                            v-model="tenantIntroMessage"
                            :rules="[formRules.ruleIntroMessage]"
                            outlined
                            label="Intro Message to Tenant"
                            counter="800"
                            variant="outlined"
                        />
                    </v-col>
                    <v-col>
                        <v-textarea
                            v-model="vendorIntroMessage"
                            :rules="[formRules.ruleIntroMessage]"
                            outlined
                            label="Intro Message to Vendor"
                            counter="800"
                            variant="outlined"
                            rows="8"
                        />
                    </v-col>
                </v-row>
            </div>

        </v-slide-y-transition>

    </v-alert>
</template>

<script setup>
// Imports

// Data
import { useRequest } from "~/composables/useRequest"
import { useSnackbarStore } from "~/store/snackbarStore"
import { useFormRules } from "~/composables/rules"
import { useUserStore } from "~/store/userStore"

const props = defineProps({
    conversation: {
        type: Object,
        required: true,
    },
})

const formRules = useFormRules()
const emits = defineEmits(['refreshConversation'])
const assigning = ref(false)
const vendors = ref([])
const selectRef = ref(null)
const snackbar = useSnackbarStore()
const auth = useUserStore()
const editIntroMessages = ref(true)
const selectedVendor = ref(null)

const tenantIntroMessage = ref('')

const vendorIntroMessage = ref(`Hey there! I'm here on part of the ${ auth.authUser.company?.name } team.
I have a tenant who is requesting some help.

Tenant: ${ props.conversation.tenant?.name }
Address: ${ props.conversation.tenant?.address }

You are now connected with the tenant and can communicate directly with them here.`)


// Lifecycle
watch(selectedVendor, (newVendor, oldVendor) => {
    if (!oldVendor && newVendor) {
        editIntroMessages.value = true
    }
    tenantIntroMessage.value = `Hey there! I'm here on part of the ${ auth.authUser.company?.name } team.
I've informed the vendor${ selectedVendor.value ? `, ${ selectedVendor.value?.name },` : '' } of your situation.

You are now connected with the vendor and can communicate directly with them here.`
}, { immediate: true })


onMounted(() => {
    fetchVendors()
})
// Methods
const selectVendor = (item) => {
    if (item.value.has_opted_in) {
        selectedVendor.value = item.value
        selectRef.value.$el.blur()
    }
}
const assignVendor = async () => {
    // console.log({
    //                     vendor: selectedVendor.value?.id,
    //             tenant_intro_message: tenantIntroMessage.value,
    //             vendor_intro_message: vendorIntroMessage.value,
    // })
    // return
    if (!selectedVendor.value?.has_opted_in || !selectedVendor.value?.id) {
        alert("Choose another vendor")
        return
    }

    try {
        assigning.value = true
        const response = useRequest(`/conversations/${ props.conversation.id }/assign_vendor/`, {
            method: 'POST',
            body: {
                vendor: selectedVendor.value?.id,
                tenant_intro_message: tenantIntroMessage.value,
                vendor_intro_message: vendorIntroMessage.value,
            }
        })
        await response.execute()
        if (response.error?.value) {
            throw(response.error.value)
        }
        emits('refreshConversation')
    } catch (error) {
        snackbar.displaySnackbar('error', "Error assigning vendor")
    } finally {
        assigning.value = false
    }
}
const fetchVendors = async () => {
    try {
        const response = useRequest('/vendors/?page_size=1000')
        await response.execute()
        if (response.error?.value) {
            throw(response.error.value)
        }
        vendors.value = response.data.value.results.filter((item) => item.active || !item.has_opted_in)
    } catch (error) {
        console.error(error)
        snackbar.displaySnackbar('error', "Error getting all vendors. Please refresh.")
    }
}

// Hooks
</script>

<style scoped lang="stylus">

</style>
