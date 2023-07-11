<template>

  <v-slide-y-transition>
    <v-container v-if="showIntro">
      <v-alert
        color="primary"
        border="start"
        variant="tonal"
        class="mt-3"
      >
        <v-chip color="success" class="font-weight-bold absolute top right mt-2 mr-2" variant="flat" size="small">
          ✨ Beta
        </v-chip>
        <div class="font-28">
          <span class="font-weight-black">PropConnect:</span>
          Settings
        </div>
        <br>
        <br>
        <div class="font-16">
          We're still in beta, so please let us know if you have any feedback or suggestions.
          <br>
          <br>
          Email: {{ auth?.authUser?.email }}
          <br>
          <br>
          Company: {{ auth?.authUser?.company?.name }}
          <br>
          <br>
          Subscription: Basic Plan - ${{ auth?.authUser?.company?.current_subscription?.price }}/month
          <br>
          <br>
          <div class="font-14">

            If you need to cancel, feel free to reach out to us at <a href="mailto:sam@ckcollab.com"
                                                                      class="text-decoration-underline">sam@ckcollab.com</a>
          </div>

        </div>
      </v-alert>
    </v-container>

  </v-slide-y-transition>
</template>

<script setup>
import { useUserStore } from "../store/userStore"

definePageMeta({
  middleware: ["auth"],
  layout: 'protected'
})

const showIntro = ref(false)
const auth = useUserStore()

onMounted(() => {
  showIntro.value = true
})

</script>

<style lang="scss" scoped>
</style>
