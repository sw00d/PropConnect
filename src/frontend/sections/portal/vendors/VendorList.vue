<template>

    <v-slide-y-transition>
        <v-container v-if="showIntro">
            <v-alert
                color="primary"
                border="start"
                variant="tonal"
                class="mt-3"
            >
                <v-chip color="success" class="font-weight-bold absolute top right mt-2 mr-2" variant="flat"
                        size="small">
                    ✨ Beta
                </v-chip>
                <div class="font-28">
                    <span class="font-weight-black">PropConnect:</span>
                    Onboarding Vendors
                </div>
                <br>
                <br>
                We understand the apprehensions around onboarding vendors – but with PropConnect, it's as
                straightforward as it gets! Our system is crafted for simplicity, ensuring smooth interactions every
                step of the way. Here's a brief rundown:
                <br>
                <br>
                <b>1) Quick Vendor Additions:</b> Add vendors by clicking the <i>Add Vendor</i> button below.
                <br>
                <br>
                <b>2) Opting In:</b> As soon as you add a vendor, they'll be pinged with a text message, inviting them
                to opt in.
                <br>
                <br>
                <b>3) Seamless Integration: </b> Once they've opted in, they're all set to tackle any tenant issues
                thrown their way.
                <br>
                <br>
                <b>4) Direct Communication:</b> When a vendor gets assigned to a tenant issue, they'll receive a text
                message that is a direct
                line of
                communication between them and the tenant.
                They can use this to ask the tenant questions, get more information, schedule a visit, or even send
                pictures/videos
                of the
                issue.
                <br>
                <br>
                <b>5) Conversation Oversight:</b> Peek into all active and past dialogues under the
                <nuxt-link to="/conversations">
                    <b class="text-decoration-underline">Conversations</b>
                </nuxt-link>
                tab.
                <br>
                <br>
                <b>Pro tip:</b> Kickstart the onboarding by enlisting yourself as a vendor. Prompt a friend to shoot a
                text to your hotline – this way, you can firsthand grasp the vendor's experience, ensuring everything's
                up to par.

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
                        <v-col class="d-flex align-center">
                            <v-list-item>
                                <v-list-item-content>
                                    <v-list-item-title class="font-weight-bold">{{ vendor.name }}</v-list-item-title>
                                    <v-list-item-title>{{ vendor.number }}</v-list-item-title>
                                    <v-list-item-subtitle>
                                        {{
                                            Object.values(vendorOptions).find((v) => v.value === vendor.vocation).label
                                        }}
                                    </v-list-item-subtitle>
                                </v-list-item-content>
                            </v-list-item>

                            <v-alert
                                v-if="!vendor.has_opted_in"
                                color="warning"
                                border="start"
                                variant="tonal"
                                class="mt-3 mx-4"
                            >

                                <div
                                    class="d-flex text-warning font-weight-bold align-center justify-space-between h-100"
                                >
                                    <div>
                                        A text invitation to join our service has been sent to the vendor. We are
                                        currently awaiting their response.
                                    </div>
                                    <v-btn
                                        :loading="resending === vendor.id"
                                        variant="flat"
                                        color="warning"
                                        size="small"
                                        height="28px"
                                        class="text-underline ml-2 cursor-pointer text-white ml-10"
                                        rounded="sm"
                                        @click="resend_opt_in(vendor)"
                                    >
                                        <span class="font-14 font-weight-regular">

                                            Resend opt in text
                                        </span>
                                    </v-btn>
                                </div>
                            </v-alert>

                        </v-col>
                        <v-col cols="2" class="d-flex align-center">
                            <v-switch
                                v-model="vendor.active"
                                @change="toggleActive(vendor)"
                                color="success"
                                hide-details
                                :disabled="!vendor.has_opted_in"
                            ></v-switch>
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
const resending = ref(null)

const vendorOptions = [
    { label: 'Plumber', value: 'plumber' },
    { label: 'Electrician', value: 'electrician' },
    { label: 'Handyman', value: 'handyman' },
    { label: 'Appliance Specialist', value: 'appliance specialist' },
    { label: 'HVAC specialist', value: 'HVAC specialist' },
    { label: 'Locksmith', value: 'locksmith' },
    { label: 'Flooring Specialist', value: 'flooring specialist' },
    { label: 'Painter', value: 'painter' },
    { label: 'Drywall Specialist', value: 'drywall specialist' },
    { label: 'Landscaper', value: 'landscaper' },
    { label: 'Other', value: 'other' },
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

onMounted(() => {
    fetchVendors()
    animate.value = true
    setTimeout(() => {
        showIntro.value = true
    }, 500)
})

const toggleActive = async (vendor) => {
    try {
        const response = await useRequest(`/vendors/${ vendor.id }/`, {
            method: "PATCH",
            body: { active: vendor.active }
        })

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

const resend_opt_in = async (vendor) => {
    try {
        resending.value = vendor.id
        const response = await useRequest(`/vendors/${ vendor.id }/resend_opt_in/`, {
            method: "POST",
        })

        if (response.error?.value) {
            throw(response.error.value)
        }
        // snackbar
        const snackbar = useSnackbarStore()
        snackbar.displaySnackbar('success', 'Opt in text sent successfully.')
    } catch (error) {
        console.error(error)
        // snackbar
        const snackbar = useSnackbarStore()
        snackbar.displaySnackbar('error', 'Something went wrong. Please try again.')
    } finally {
        resending.value = null
    }
}
</script>
