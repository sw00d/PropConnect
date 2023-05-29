<template>
  <div>
    <v-btn
      @click="navigateTo('/dashboard')"
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
    <v-row v-else class="fade-in mt-10">
      <v-col md="6" xs="12" sm="12" class="bg">
        <v-card>
          <v-card-title>
            Conversation Details
          </v-card-title>

          <v-card-text>

            <div class="py-1 my-4 border-b border-t d-flex justify-space-between">
              <div>
                Date started:
              </div>
              <div>

                {{ dayjs(conversation.date_created).format('MMM D, YYYY - H:mma') }}
              </div>
            </div>

            <div class="py-1 my-4 border-b border-t d-flex justify-space-between">
              <div>
                Tenant:
              </div>
              <div>
                {{ conversation.tenant?.name || "No Name" }} ({{
                  $formatPhoneNumber(conversation.tenant.number)
                }})
              </div>
            </div>

            <div class="py-1 my-4 border-b border-t d-flex justify-space-between">
              <div>
                Vendor:
              </div>
              <div>
                {{ conversation.vendor?.name || "No Name" }} ({{
                  $formatPhoneNumber(conversation.vendor.number)
                }})
              </div>
            </div>

            <div class="py-1 my-4 border-b border-t d-flex justify-space-between">
              <div>
                Status:
              </div>
              <div>
                {{ conversation.is_active ? "Active" : "Inactive" }}
              </div>
            </div>
          </v-card-text>
        </v-card>
        <!--      {{ conversation }}-->
      </v-col>
      <v-col md="6" sm="12">
        <v-chip
          class="mr-3"
          @click="switchConversationView('assistant')"
          :variant="activeConversation === 'assistant' ? 'outlined' : 'default'"
        >
          Assistant
        </v-chip>
        <v-chip
          @click="switchConversationView('vendor')"
          :variant="activeConversation === 'vendor' ? 'outlined' : 'default'"
        >
          Vendor
        </v-chip>

        <v-sheet class="border pa-3 rounded-lg mt-4 overflow-auto bg-background" max-height="80vh">
          <div
            v-for="(message,i) in conversation.messages"
            :key="i"
            class="d-flex flex-column"
          >
            <div v-if="message.role === 'user'" class="left-msg">
              <div class="font-12 text-highContrast">
                {{ conversation.tenant?.name || `Tenant ${ $formatPhoneNumber(conversation.tenant.number) }` }}
              </div>
              <div class="rounded-lg pa-2 bg-surfaceSecondary">
                {{ message.message_content }}
              </div>
            </div>

            <div v-else-if="message.role === 'assistant'" class="right-msg mt-3">
              <div class="font-12 text-highContrast text-right">Bot Assistant</div>
              <div class="rounded-lg pa-2 bg-primary">
                {{ message.message_content }}
              </div>
            </div>
          </div>
        </v-sheet>

      </v-col>
    </v-row>
  </div>

</template>

<script setup>
import { useRoute } from 'vue-router'
import { useRequest } from "../../composables/useRequest"
import { ref, onMounted } from 'vue'
import dayjs from "dayjs"

const { $formatPhoneNumber } = useNuxtApp()

definePageMeta({
  layout: 'default'
})
const route = useRoute()
const { id } = route.params

const conversation = ref({})
const loading = ref(true)
const activeConversation = ref('assistant')

const fetchConversations = async (param_id) => {
  try {
    const { data, error, execute } = useRequest(`/conversations/${ param_id }`)
    await execute()
    conversation.value = data.value
    console.log(toRaw(conversation.value.messages))
  } catch (error) {
    console.error(error)
  } finally {
    setTimeout(() => loading.value = false, 1000)
    // loading.value = false
  }
}
const switchConversationView = (view) => {
  activeConversation.value = view
}

onMounted(() => fetchConversations(id))

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
