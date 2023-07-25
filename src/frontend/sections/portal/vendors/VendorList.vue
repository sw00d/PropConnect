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
          Onboarding Vendors
        </div>
        <br>
        <br>
        Onboarding your vendors can be scary, we get it! But don't worry, our system is simple and seamless to interact
        with. All your vendors need is a number they can text from and they're ready to go! Here's what you should know:
        <br>
        <br>
        <b>1)</b> Add vendors by clicking the <i>Add Vendor</i> button below.
        <br>
        <br>
        <b>2)</b> Once you add a vendor, they'll be in our system and ready to take on your tenants issues.
        <br>
        <br>
        <b>3)</b> When a vendor gets assigned to a tenant issue, they'll receive a text message that is a direct line of
        communication between them and the tenant.
        They can use this to ask questions, get more information, schedule a visit, or even send pictures/videos of the
        issue.
        <br>
        <br>
        <b>4)</b> You can view all conversations in the
        <nuxt-link to="/conversations">
          <b class="text-decoration-underline">Conversations</b>
        </nuxt-link>
        tab.
        <br>
        <br>
        <b>Pro tip:</b> Before you start onboarding vendors/tenants, add yourself as a vendor and have a friend text
        your hotline just so you can understand the experience your vendors will be having.

      </v-alert>
    </v-container>

  </v-slide-y-transition>

  <v-slide-y-transition>
    <v-container v-if="animate">
      <v-card>
        <v-card-title class="font-weight-black font-24">Add vendor</v-card-title>
        <v-card-text class="mt-4">
          <v-form @submit.prevent="createVendor">
            <div>
              <v-row class="flex-column flex-md-row">
                <v-col md="6">
                  <v-text-field
                    v-model="newVendor.name"
                    label="Vendor Name"
                    required
                    :error="errors.name"
                    :error-messages="errors.name"
                  ></v-text-field>
                </v-col>
                <!--                <v-col md="6">-->
                <!--                  <v-text-field-->
                <!--                    v-model="newVendor.company_name"-->
                <!--                    label="Workplace (optional)"-->
                <!--                  ></v-text-field>-->
                <!--                </v-col>-->

                <v-col md="6">
                  <v-select
                    v-model="newVendor.vocation"
                    label="Vocation/Profession"
                    :items="vendorOptions"
                    item-title="label"
                    item-value="value"
                    :error="errors.vocation"
                    :error-messages="errors.vocation"
                  ></v-select>
                </v-col>
                <v-col md="6">
                  <PhoneNumberField
                    :value="newVendor.number"
                    @input="newVendor.number = $event"
                  />
                  <!--                  <v-text-field-->
                  <!--                    v-model="newVendor.number"-->
                  <!--                    label="Number"-->
                  <!--                    required-->
                  <!--                    :error="errors.number"-->
                  <!--                    :error-messages="errors.number"-->
                  <!--                  ></v-text-field>-->
                </v-col>
              </v-row>

              <div>
                <v-btn
                  type="submit"
                  height="48px"
                  color="primary"
                  size="large"
                  class="mt-4"
                  :loading="creating"
                  :disabled="!newVendor.number || !newVendor.name || !newVendor.vocation"
                >
                  Add vendor
                </v-btn>
              </div>
            </div>
          </v-form>
        </v-card-text>
      </v-card>

      <v-card class="mt-10">
        <v-card-text class="-4">
          <v-row>
            <v-col cols="10" class="font-weight-black">Vendor</v-col>
            <v-col cols="2" class="font-weight-black">Active</v-col>
          </v-row>

          <v-row
            v-for="vendor in vendors"
            :key="vendor.id"
          >
            <v-col cols="10">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title class="font-weight-bold">{{ vendor.name }}</v-list-item-title>
                  <v-list-item-title>{{ vendor.number }}</v-list-item-title>
                  <v-list-item-subtitle>{{ vendor.vocation }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="2">
              <v-switch v-model="vendor.active" @change="toggleActive(vendor)" color="success"></v-switch>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

    </v-container>
  </v-slide-y-transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRequest } from "../../../composables/useRequest"
import { useSnackbarStore } from "../../../store/snackbarStore"
import { useUserStore } from "../../../store/userStore"
import PhoneNumberField from "../../../components/PhoneNumberField/PhoneNumberField.vue"

const vendors = ref([])
const newVendor = ref({ name: '', number: '' })
const animate = ref(false)
const errors = ref({})
const auth = useUserStore()
const creating = ref(false)
const showIntro = ref(false)

const vendorOptions = [
  // These values have to be very specific because they are used to filter vendors via GPT
  // When adding more, thoroughly test on backend
  {label:'Plumber', value: 'plumber'},
  {label:'Electrician', value: 'electrician'},
  {label:'Handyman', value: 'handyman'},
  {label:'Appliance Specialist', value: 'appliance specialist'},
  {label:'HVAC specialist', value: 'air-condition specialist'},
  {label:'Locksmith', value: 'locksmith'},
  {label:'Flooring Specialist', value: 'flooring specialist'},
  {label:'Painter', value: 'painter'},
  {label:'Drywall Specialist', value: 'drywall specialist'},
  {label:'Carpenter', value: ''},
  {label:'Roofer', value: ''},
  {label:'Landscaper', value: ''},
]

const createVendor = async () => {
  try {
    creating.value = true
    errors.value = {} // Reset errors

    const res = await useRequest('/vendors/', {
      method: "POST",
      body: {
        ...newVendor.value,
        number: `+1${ newVendor.value.number }`,
        company: auth.authUser.company.id
      }
    })
    if (res.error?.value) {
      throw(res.error.value)
    } else {
      // snackbar
      const snackbar = useSnackbarStore()
      snackbar.displaySnackbar('success', 'Vendor added successfully.')
    }
    newVendor.value = { name: '', company_name: '', number: '' }
    await fetchVendors()  // refresh the list of vendors
  } catch (error) {
    errors.value = error.value.data
    console.error(error)
  } finally {
    creating.value = false
  }
}

const fetchVendors = async () => {
  try {
    const response = useRequest('/vendors/?page_size=1000')
    await response.execute()
    if (response.error?.value) {
      throw(response.error.value)
    }
    vendors.value = response.data.value.results
  } catch (error) {
    console.error(error)
  }
}

const toggleActive = async (vendor) => {
  try {
    const response = await useRequest(`/vendors/${ vendor.id }/`, { method: "PATCH", body: { active: vendor.active } })

    if (response.error?.value) {
      vendor.active = !vendor.active
      throw(response.error.value)
    }
    fetchVendors()  // refresh the list of vendors
    // vendors.value = response.data.value.results
  } catch (error) {
    console.error(error)
    // snackbar
    const snackbar = useSnackbarStore()
    snackbar.displaySnackbar('error', 'Something went wrong. Please try again.')
  }
}

onMounted(() => {
  fetchVendors()
  animate.value = true
  setTimeout(() => {
    showIntro.value = true
  }, 500)
})

</script>
