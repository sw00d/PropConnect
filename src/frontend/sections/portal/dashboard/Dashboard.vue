<template>
  <v-container class="h-100 d-flex flex-column">
    <div>
      <v-slide-y-transition>
        <v-card v-if="mounted.header" class="py-4">
          <v-card-title class="d-flex justify-space-between align-center h-100 font-20 flex-wrap">
            <div class="text-capitalize">
              {{ user.authUser?.company?.name }}
            </div>
            <div>
              <div>
                <div class="font-12 lh-12 mt-10 mt-md-0">
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
                  {{ company.assistant_phone_number }}
                  <v-btn @click="$copyTextToClipboard(company.assistant_phone_number)" icon>
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
          <b>1)</b> You now have a dedicated AI hotline, <b>{{ company.assistant_phone_number }}</b>. This is the number
          your tenants will
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
          things and know what your tenants and vendors will experience.

        </v-alert>
      </v-slide-y-transition>

      <v-row class="mt-4 flex-column flex-md-row">
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
                  Coming soon
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
                <nuxt-link to="/vendors">

                  <v-btn class="d-flex align-center bg-primary font-14" width="80px" height="40px">
                    New
                  </v-btn>
                </nuxt-link>
              </v-card-title>
              <v-card-text class="d-flex align-center">
                <v-sheet width="50%" max-height="300px">
                  <v-img :src="vendorImg"/>
                </v-sheet>
                <div class="text-body-1 font-weight-bold d-flex justify-center ml-10">
                  Coming soon
                </div>
              </v-card-text>
            </v-card>
          </v-slide-x-reverse-transition>

          <v-slide-x-reverse-transition>
            <v-card v-if="mounted.rightBottomCard" class="mt-4 d-flex flex-column" height="302px">
              <v-card-title class="d-flex justify-space-between align-center">
                <div>
                  Costs and Usage
                </div>
                <div class="text-body-2 font-weight-medium">
                  Coming soon
                </div>
              </v-card-title>
              <v-sheet height="80%">
                <v-img :src="openingSoon"/>
              </v-sheet>
              <!--              <div class="d-flex align-end pb-4">-->
              <!--                <v-row>-->
              <!--                  <v-spacer/>-->
              <!--                  <v-col class="pl-8 hidden-sm-and-down">-->
              <!--                    <div class="font-weight-bold">Breakdown</div>-->
              <!--                  </v-col>-->
              <!--                </v-row>-->
              <!--              </div>-->

              <!--              <v-card-text class="d-flex align-md-center justify-space-between flex-1 flex-wrap pt-0 flex-column flex-md-row">-->
              <!--                <div class="text-center flex-1">-->
              <!--                  <div class="text-h3 text-primary font-weight-black">-->
              <!--                    $40.20-->
              <!--                  </div>-->
              <!--                  <span class="font-12 font-weight-medium">Next billing date 12/5/2023</span>-->
              <!--                </div>-->

              <!--                <v-divider vertical class="hidden-sm-and-down"/>-->

              <!--                <div class="flex-1 ml-6 d-flex flex-column align-start justify-start h-100 mt-6 mt-md-0">-->
              <!--                  <v-row class="w-100" no-gutters="">-->

              <!--                    <v-col cols="7" class="font-12">-->
              <!--                      Conversations-->
              <!--                    </v-col>-->
              <!--                    <v-col class="d-flex justify-space-between font-weight-bold">-->
              <!--                      <v-divider class="divider" vertical></v-divider>-->
              <!--                      45-->
              <!--                    </v-col>-->
              <!--                  </v-row>-->

              <!--                  <v-row class="w-100" no-gutters="">-->
              <!--                    <v-col cols="7" class="font-12">-->
              <!--                      Cost/Conversation-->
              <!--                    </v-col>-->
              <!--                    <v-col class="d-flex justify-space-between font-weight-bold">-->
              <!--                      <v-divider class="divider" vertical></v-divider>-->
              <!--                      $0.45-->
              <!--                    </v-col>-->
              <!--                  </v-row>-->

              <!--                  <v-row class="w-100" no-gutters="">-->

              <!--                    <v-col cols="7" class="font-12">-->
              <!--                      Base subscription-->
              <!--                    </v-col>-->
              <!--                    <v-col class="d-flex justify-space-between font-weight-bold">-->
              <!--                      <v-divider class="divider" vertical></v-divider>-->
              <!--                      ${{ subscriptionPrice }}-->
              <!--                    </v-col>-->
              <!--                  </v-row>-->

              <!--                  <v-row class="w-100" no-gutters="">-->

              <!--                    <v-col cols="7" class="font-14 font-weight-bold">-->
              <!--                      Total-->
              <!--                    </v-col>-->
              <!--                    <v-col class="d-flex justify-space-between font-weight-bold">-->

              <!--                      <v-divider class="divider" vertical></v-divider>-->

              <!--                      $44.99-->
              <!--                    </v-col>-->
              <!--                  </v-row>-->
              <!--                </div>-->
              <!--              </v-card-text>-->
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
import openingSoon from "~/assets/portal/opening-soon.png"

// Data
const user = useUserStore()
const mounted = ref({
  header: false,
  leftCard: false,
  rightTopCard: false,
  rightBottomCard: false,
})
const showInfo = ref(false)
const company = computed(() => user.authUser.company)

// Lifecycle
onMounted(() => {
  setTimeout(() => {
    mounted.value.header = true
  }, 500)

  setTimeout(() => {
    mounted.value.leftCard = true
  }, 700)

  setTimeout(() => {
    mounted.value.rightTopCard = true
  }, 900)

  setTimeout(() => {
    mounted.value.rightBottomCard = true
  }, 1100)

  setTimeout(() => {
    mounted.value.rightBottomCard = true
    if (user.hasActiveSubscription) {
      showInfo.value = true
    }
  }, 1300)

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
