<template>
  <AuthContentContainer :image="beachHouse">
    <template #default>
      <div>
        <div class="text-h4 font-weight-black text-primary">Welcome, {{ auth.authUser?.first_name }}!</div>
        <div class="mb-6 mt-2">
          Let's hear a bit about your workplace!
        </div>

        <v-form :model-value="valid" @submit.prevent="onSubmit">
          <v-text-field
            v-model="companyName"
            label="Company Name"
            :rules="nameRules"
            :error-messages="errors.company_name"
            :error="errors.company_name"
          />

          <v-text-field
            v-model="website"
            label="Company Website"
            class="my-1"
            :error-messages="errors.website"
            :error="errors.website"
          />
          <v-row no-gutters>
            <v-col cols="6">
              <v-select
                v-model="numberOfDoors"
                :rules="numOfDoorsRules"
                hint="How many doors will we manage for you?"
                persistent-hint
                label="Number of doors"
                :items="numberOfDoorsOptions"
                class="mr-2"
                :error-messages="errors.number_of_doors"
                :error="errors.number_of_doors"
                :loading="fetchingOptions"
                item-title="display_name"
                item-value="display_name"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                class="ml-2"
                v-model="zip"
                label="Zip Code"
                :error-messages="errors.zip_code"
                :error="errors.zip_code"
                :rules="zipRules"
                type="number"
              />
            </v-col>
          </v-row>
          <v-slide-y-transition>
            <v-alert
              v-if="showAlert"
              color="highlight"
              border="start"
              variant="tonal"
              class="mt-3"
            >
              We are still in <strong>beta</strong> and are best suited for managing 200 doors or less.
              <strong> Expect limited functionality. </strong>
              <br>
              <br>
              However, we would love to chat about a custom solution for you. Reach out to us directly at
              <strong class="text-decoration-underline">
                <a href="mailto:sam@ckcollab.com">sam@ckcollab.com</a>
              </strong>.
            </v-alert>
          </v-slide-y-transition>
          <v-btn
            type="submit"
            :color="valid ? 'primary' : null"
            class="mt-3"
            width="100%"
            :disabled="!valid"
            :loading="submitting"
          >
            Finish
          </v-btn>
        </v-form>
      </div>
    </template>
  </AuthContentContainer>
</template>

<script setup lang="ts">
// Imports
import beachHouse from "@/assets/signup/beach-house.png"
import AuthContentContainer from "~/components/Containers/AuthContentContainer.vue";
import {useUserStore} from "~/store/userStore";
import {useSnackbarStore} from "~/store/snackbarStore";
import {useRequest} from "~/composables/useRequest";

// Data
const router = useRouter();
const auth = useUserStore()
const companyName = ref('')
const website = ref('')
const zip = ref('')
const numberOfDoors = ref('1-50')
const numberOfDoorsOptions = ref([])
const errors = ref({});
const submitting = ref<boolean>(false);
const fetchingOptions = ref<boolean>(false);

const showAlert = computed(() => {
  if (
    numberOfDoors.value === '1-50' ||
    numberOfDoors.value === '50-200'
  ) {
    return false
  } else {
    return true
  }
})

const nameRules = [
  (v: string) => !!v || 'Company name is required',
];

const numOfDoorsRules = [
  (v: string) => !!v || 'Field required',
];

// zip: value => (/^\d{5}$/).test(value) || 'Invalid zip code.',
const zipRules = [
  (value: string) => (/^\d{5}$/).test(value) || 'Invalid zip code.',
];

const valid = computed(() => {
  return !!companyName.value && !!numberOfDoors.value && !!zip.value &&
    nameRules.every(rule => rule(companyName.value) === true) &&
    numOfDoorsRules.every(rule => rule(numberOfDoors.value) === true) &&
    zipRules.every(rule => rule(zip.value) === true)
});

// Lifecycle
onMounted(() => {
  getCompanySizeOptions()
})

// Methods
const getCompanySizeOptions = async () => {
  fetchingOptions.value = true
  const res = await useRequest('companies/', {
    method: 'options'
  })
  await res.execute()

  if (res.error?.value) {
    const snackbar = useSnackbarStore()
    snackbar.displaySnackbar('error', "Error signing up. Please try again later.")
  }

  numberOfDoorsOptions.value = res.data?.value?.actions?.POST?.number_of_doors?.choices || ['1-50']
  fetchingOptions.value = false
}

const onSubmit = async () => {
  submitting.value = true
  const data = {
    name: companyName.value,
    website: website.value,
    zip_code: zip.value,
    number_of_doors: numberOfDoors.value
  }
  const res = await useRequest('companies/', {
    method: 'post',
    body: data
  })
  await res.execute()

  await auth.fetchUser() // refresh user

  if (res.error?.value) {
    errors.value = res.error.value.data
    if (res.error.value.statusCode !== 400) {
      const snackbar = useSnackbarStore()
      snackbar.displaySnackbar('error', "Error signing up. Please try again later.")
    }
    submitting.value = false
  } else {
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  }
}

// Hooks
</script>

<style scoped lang="stylus">

</style>
