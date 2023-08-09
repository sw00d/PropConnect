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
    </v-alert>
</template>

<script setup>
// Imports

// Data
import { useRequest } from "~/composables/useRequest"
import { useSnackbarStore } from "~/store/snackbarStore"

const props = defineProps({
    conversation: {
        type: Object,
        required: true,
    },
})
const emits = defineEmits(['refreshConversation'])
const assigning = ref(false)
const vendors = ref([])
const selectedVendor = ref(null)
const selectRef = ref(null)
const snackbar = useSnackbarStore()

// Lifecycle
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
