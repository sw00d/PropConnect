<template>
  <v-container class="h-100 d-flex flex-column">
    <div>
      <v-slide-y-transition>
        <v-card v-if="mounted.header" class="py-4">
          <v-card-title class="d-flex justify-space-between align-center h-100 font-20">
            <div class="text-capitalize">
              {{ user.authUser?.company?.name }} Property Management
            </div>
            <div>
              <div>
                <div class="font-12 lh-12">
                  Your hotline
                  <v-btn
                    @click="showInfo = !showInfo"
                    icon
                    width="20px"
                    height="20px"
                    rounded="xl"
                  >
                    <v-icon>mdi-info</v-icon>
                  </v-btn>
                </div>
                <div class="font-20">
                  +1 (208) 283-2039
                  <v-btn @click="$copyTextToClipboard('+1 (208) 283-2039')" icon>
                    <v-icon size="18">mdi-content-copy</v-icon>
                  </v-btn>
                </div>
              </div>
            </div>
          </v-card-title>
        </v-card>
      </v-slide-y-transition>

      <v-slide-y-transition>
        <v-alert
          v-if="showInfo"
          color="primary"
          border="start"
          variant="tonal"
          class="mt-3"
        >
          <v-chip color="success" class="font-weight-bold absolute top right mt-2 mr-2" variant="flat" size="small">
            ✨ Beta
          </v-chip>
          <div class="font-28">
            Welcome to
            <span class="font-weight-black">PropConnect</span>
            🎉
          </div>
          <br>
          How it works:
          <br>
          <br>
          <b>1)</b> You now have a dedicated AI hotline, <b>+1 (208) 283-2039</b>. This is the number your tenants will
          text when wanting to submit a maintenance request
          <br>
          <br>
          <b>2)</b> Once our AI has gotten enough information from the tenant, the tenant and vendor will be connected
          via a secondary phone number.
          Both the vendor and tenant will get an introduction text, making sure each party knows who and what the
          conversation is about.
          <br>
          <br>
          <b>3)</b> From there, both the tenant and vendor can directly text each other using this secondary number.
          <br>
          <br>
          <b>4)</b> You can view all conversations in the
          <nuxt-link to="/conversations">
            <b class="text-decoration-underline">Conversations</b>
          </nuxt-link>
          tab.
          <br>
          <br>
          <b>Pro tip:</b> Before adding any vendors, you should text your hotline just to get a feel for
          things and know what your tenants will experience.

        </v-alert>
      </v-slide-y-transition>

      <v-row class="mt-4">
        <v-col>
          <v-slide-x-transition>
            <v-card v-if="mounted.leftCard" height="620px">
              <v-card-title class="d-flex justify-space-between">
                <div>
                  Conversations
                </div>
                <!--                <v-btn class="d-flex align-center bg-primary font-14" width="80px" height="40px">-->
                <!--                  New-->
                <!--                </v-btn>-->
              </v-card-title>
              <v-card-text class="d-flex align-center justify-center mt-16 flex-column flex-1 relative">
                <div class="text-body-1 font-weight-bold">
                  No conversations yet
                </div>
                <v-sheet width="80%">
                  <v-img :src="convoImg"/>
                </v-sheet>
              </v-card-text>
            </v-card>
          </v-slide-x-transition>
        </v-col>

        <v-col class="d-flex flex-column">
          <v-slide-x-reverse-transition>
            <v-card v-if="mounted.rightTopCard" height="302px">
              <v-card-title class="d-flex justify-space-between">
                <div>
                  Vendors
                </div>
                <v-btn class="d-flex align-center bg-primary font-14" width="80px" height="40px">
                  New
                </v-btn>
              </v-card-title>
              <v-card-text class="d-flex align-center">
                <v-sheet width="50%" max-height="300px">
                  <v-img :src="vendorImg"/>
                </v-sheet>
                <div class="text-body-1 font-weight-bold d-flex justify-center ml-10">
                  No vendors yet
                </div>
              </v-card-text>
            </v-card>
          </v-slide-x-reverse-transition>

          <v-slide-x-reverse-transition>
            <v-card v-if="mounted.rightBottomCard" class="mt-4 d-flex flex-column" height="302px">
              <v-card-title class="d-flex justify-space-between align-center">
                <div>
                  Usage
                </div>
                <div class="text-green text-body-2 font-weight-medium">
                  -2.5% change
                </div>
              </v-card-title>
              <div class="d-flex align-end pb-4">
                <v-row>
                  <v-spacer/>
                  <v-col class="pl-8">
                    <div class="font-weight-bold">Breakdown</div>
                  </v-col>
                </v-row>
              </div>

              <v-card-text class="d-flex align-center justify-space-between flex-1 flex-wrap pt-0">
                <div class="text-center flex-1">
                  <div class="text-h3 text-primary font-weight-black">
                    $40.20
                  </div>
                  <span class="font-12 font-weight-medium">Next billing date 12/5/2023</span>
                </div>

                <v-divider vertical/>

                <div class="flex-1 ml-6 d-flex flex-column align-start justify-start h-100">
                  <v-row class="w-100" no-gutters="">

                    <v-col cols="7" class="font-12">
                      Conversations
                    </v-col>
                    <v-col class="d-flex justify-space-between font-weight-bold">
                      <v-divider class="divider" vertical></v-divider>
                      45
                    </v-col>
                  </v-row>

                  <v-row class="w-100" no-gutters="">
                    <v-col cols="7" class="font-12">
                      Cost/Conversation
                    </v-col>
                    <v-col class="d-flex justify-space-between font-weight-bold">
                      <v-divider class="divider" vertical></v-divider>
                      $0.45
                    </v-col>
                  </v-row>

                  <v-row class="w-100" no-gutters="">

                    <v-col cols="7" class="font-12">
                      Base subscription
                    </v-col>
                    <v-col class="d-flex justify-space-between font-weight-bold">
                      <v-divider class="divider" vertical></v-divider>
                      ${{ subscriptionPrice }}
                    </v-col>
                  </v-row>

                  <v-row class="w-100" no-gutters="">

                    <v-col cols="7" class="font-14 font-weight-bold">
                      Total
                    </v-col>
                    <v-col class="d-flex justify-space-between font-weight-bold">

                      <v-divider class="divider" vertical></v-divider>

                      $44.99
                    </v-col>
                  </v-row>
                </div>
              </v-card-text>
            </v-card>
          </v-slide-x-reverse-transition>
        </v-col>
      </v-row>
    </div>

  </v-container>
</template>

<script setup lang="ts">
// Imports
import {useUserStore} from "~/store/userStore";
import {onMounted} from "vue";
import convoImg from "~/assets/portal/convo.png"
import vendorImg from "~/assets/portal/vendors.png"

// Data
const user = useUserStore()
console.log(user.authUser?.company?.current_subscription)
const mounted = ref({
  header: false,
  leftCard: false,
  rightTopCard: false,
  rightBottomCard: false,
})
const showInfo = ref(false)

const subscriptionPrice = computed(() => {
  return (parseInt(user.authUser?.company?.current_subscription?.plan?.amount_decimal) / 100).toFixed(2)
})

// Lifecycle
onMounted(() => {
  setTimeout(() => {
    mounted.value.header = true
  }, 500)

  setTimeout(() => {
    mounted.value.leftCard = true
    // showInfo.value = true
  }, 700)

  setTimeout(() => {
    mounted.value.rightTopCard = true
  }, 900)

  setTimeout(() => {
    mounted.value.rightBottomCard = true
  }, 1100)

})

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.divider {
  opacity 1
  height 20px
}
</style>
