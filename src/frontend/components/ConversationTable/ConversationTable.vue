<template>
    <v-sheet class="d-flex align-center justify-center bg-transparent" height="70vh" v-if="loading">
        <v-progress-circular
            size="64"
            indeterminate
            color="primary"
        />
    </v-sheet>
    <!--  TODO: Use server table thing from vuetify-->
    <v-data-table
        v-else
        :headers="headers"
        :items="conversations"
        item-value="name"
        class="elevation-1 w-100 rounded-lg"
        @click:row="goToConversation"
    >
        <template #item.unread="{item: { selectable }}">
            <v-sheet
                v-if="selectable.has_new_activity"
                class="bg-primary rounded-lg"
                width="10px"
                height="10px"
            />
        </template>
        <template #item.date_created="{item: { selectable }}">
            <div class="my-8 ">
                {{ dayjs(selectable.value?.date_created).format('MMM D, YYYY - H:mma') }}
            </div>
        </template>
        <template #item.tenant="{item: { selectable }}">
            <div>

                <div>{{ selectable.tenant?.name || "No Name" }}</div>
                <div class="font-12 opacity-8">
                    {{ selectable.tenant?.address }}
                </div>
                <div class="font-12 opacity-8">
                    {{ $formatPhoneNumber(selectable.tenant?.number) }}
                    <v-btn
                        @click.stop="$copyTextToClipboard($formatPhoneNumber(selectable.tenant?.number));"
                        icon
                        width="16px"
                        height="16px"
                    >
                        <v-icon size="12px">mdi-content-copy</v-icon>
                    </v-btn>
                </div>
            </div>
        </template>
        <template #item.vendor="{item: { selectable }}">
            <div v-if="!selectable.vendor">
                Not yet assigned
            </div>
            <div v-else>
                <div class="text-capitalize weight-700 font-18">{{ selectable.vendor?.vocation }}</div>
                <div class="font-14 opacity-8">{{ selectable.vendor?.name }}</div>
                <div class="font-12 opacity-8" v-if="selectable.vendor">
                    {{ $formatPhoneNumber(selectable.vendor?.number) }}
                    <v-btn
                        @click.stop="$copyTextToClipboard($formatPhoneNumber(selectable.vendor?.number));"
                        size="x-small"
                        icon
                        height="30px"
                    >
                        <v-icon>mdi-content-copy</v-icon>
                    </v-btn>
                </div>
            </div>
        </template>

        <template #item.status="{item: { selectable }}">

            <v-tooltip location="bottom">
                <template v-slot:activator="{ props }">
                    <div v-bind="props">
                        <v-icon
                            :color="selectable.is_active ? 'success' : 'error'"
                            :title="selectable.is_active ? 'Active' : 'Inactive'"
                        >
                            {{ selectable.is_active ? 'mdi-check' : 'mdi-close' }}
                        </v-icon>
                        {{ selectable.is_active ? "Active" : "Inactive" }}
                    </div>
                </template>
                Conversation automatically goes inactive after 48 hours of no messages.
            </v-tooltip>
        </template>
    </v-data-table>
</template>

<script setup>
import { VDataTable } from 'vuetify/labs/VDataTable'
import dayjs from "dayjs"


const headers = ref([
    { title: '', key: 'unread', sortable: false, width: '0px' },
    { title: 'Start Date', key: 'date_created', sortable: false },
    { title: 'Tenant', key: 'tenant', sortable: false },
    { title: 'Vendor', key: 'vendor', sortable: false },
    { title: 'Status', key: 'status', sortable: false },
])
const conversations = ref([])
const loading = ref(true)

async function fetchConversations() {
    try {
        const { data, error, execute } = useRequest('/conversations/?page_size=1000')
        await execute()

        if (error?.value) {
            throw new Error(error.value)
        }
        conversations.value = data.value.results

    } catch (error) {
        // TODO handle error with some snack bars
        errors.value = error.value.data
        snackbarStore.displaySnackbar('error', 'Error signing in')
        console.error(error)
    } finally {
        loading.value = false
    }
}

function goToConversation(_, { item: { selectable } }) {
    navigateTo('/conversations/' + selectable.id)
}


onMounted(() => fetchConversations())
</script>

<style scoped lang="stylus">
>>> tr, >>> .v-data-table-footer {
    font-size 14px
}

>>> .v-data-table-footer {
    padding 10px;
}
</style>
