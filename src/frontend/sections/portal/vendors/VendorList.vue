<template>
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

const vendorOptions = [
  'Plumber',
  'Electrician',
  'Handyman',
  'Appliance Specialist',
  'Air-condition specialist',
  'Locksmith',
  'Flooring Specialist',
  'Painter',
  'Drywall Specialist',
  'Carpenter',
  'Roofer',
  'Landscaper',
]

const createVendor = async () => {
  try {
    creating.value = true
    errors.value = {} // Reset errors

    const res = await useRequest('/vendors/', {
      method: "POST",
      body: {
        ...newVendor.value,
        number: `+1${newVendor.value.number}`,
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
})

</script>
