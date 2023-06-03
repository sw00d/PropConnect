<template>
  <v-sheet class="d-flex align-center justify-center bg-transparent" height="70vh" v-if="loading">
    <v-progress-circular
      size="64"
      indeterminate
      color="primary"
    />
  </v-sheet>
  <v-data-table
    :headers="headers"
    :items="conversations"
    item-value="name"
    class="elevation-1 w-100 rounded-lg"
    @click:row="goToConversation"
  >
    <template #item.date_created="{item}">
      <div class="my-8">
        {{ dayjs(item.value.date_created).format('MMM D, YYYY - H:mma') }}
      </div>
    </template>
    <template #item.tenant="{item}">
      <div>
        <div>{{ item.value.tenant?.name || "No Name" }}</div>
        <div>{{ $formatPhoneNumber(item.value.tenant?.number) }}</div>
      </div>
    </template>
    <template #item.vendor="{item}">
      <div>
        <div>{{ item.value.vendor?.name }}</div>
        <div>{{ $formatPhoneNumber(item.value.vendor?.number) }}</div>
      </div>
    </template>

    <template #item.status="{item}">
      <div>
        {{ item.value.is_active ? "Active" : "Inactive" }}
      </div>
    </template>
  </v-data-table>
</template>

<script setup>
import { VDataTable } from 'vuetify/labs/VDataTable'
import dayjs from "dayjs"

const { $formatPhoneNumber } = useNuxtApp()

const headers = ref([
  { title: 'Date', key: 'date_created', sortable: false },
  { title: 'Tenant', key: 'tenant', sortable: false },
  { title: 'Vendor', key: 'vendor', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
])
const conversations = ref([])
const loading = ref(true)

async function fetchConversations() {
  try {
    const { data, error, execute } = useRequest('/conversations/')
    await execute()
    conversations.value = data.value
    console.log(data.value)
  } catch (error) {
    // TODO handle error with some snack bars
    alert('Error fetching conversations')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function goToConversation(_, { item }) {
  navigateTo('/conversations/' + item.value.id)
}


onMounted(fetchConversations)
</script>

<style scoped lang="stylus">

</style>
