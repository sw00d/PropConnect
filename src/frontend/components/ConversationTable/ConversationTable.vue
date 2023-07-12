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
    <template #item.unread="{item}">
      <v-sheet
        v-if="item.value.has_new_activity"
        class="bg-primary rounded-lg"
        width="10px"
        height="10px"
      />
    </template>
    <template #item.date_created="{item}">
      <div class="my-8 ">
        {{ dayjs(item.value.date_created).format('MMM D, YYYY - H:mma') }}
      </div>
    </template>
    <template #item.tenant="{item}">
      <div>
        <div>{{ item.value.tenant?.name || "No Name" }}</div>
        <div class="font-12 opacity-8">
          {{ $formatPhoneNumber(item.value.tenant?.number) }}
          <v-btn
            @click.stop="$copyTextToClipboard($formatPhoneNumber(item.value.tenant?.number));"
            size="x-small"
            icon
          >
            <v-icon>mdi-content-copy</v-icon>
          </v-btn>
        </div>
      </div>
    </template>
    <template #item.vendor="{item}">
      <div v-if="!item.value?.vendor">
        Not yet assigned
      </div>
      <div v-else>
        <div class="text-capitalize weight-700 font-18">{{ item.value?.vendor?.vocation }}</div>
        <div class="font-14 opacity-8">{{ item.value?.vendor?.name }}</div>
        <div class="font-12 opacity-8" v-if="item.value?.vendor">
          {{ $formatPhoneNumber(item.value?.vendor?.number) }}
          <v-btn
            @click.stop="$copyTextToClipboard($formatPhoneNumber(item.value.vendor?.number));"
            size="x-small"
            icon
            height="30px"
          >
            <v-icon>mdi-content-copy</v-icon>
          </v-btn>
        </div>
      </div>
    </template>

    <template #item.status="{item}">

      <v-tooltip location="bottom">
        <template v-slot:activator="{ props }">
          <div v-bind="props">
            <v-icon
              :color="item.value.is_active ? 'success' : 'error'"
              :title="item.value.is_active ? 'Active' : 'Inactive'"
            >
              {{ item.value.is_active ? 'mdi-check' : 'mdi-close' }}
            </v-icon>
            {{ item.value.is_active ? "Active" : "Inactive" }}
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

function goToConversation(_, { item }) {
  navigateTo('/conversations/' + item.value.id)
}


onMounted(fetchConversations)
</script>

<style scoped lang="stylus">
>>> tr, >>> .v-data-table-footer {
  font-size 14px
}

>>> .v-data-table-footer {
  padding 10px;
}
</style>
