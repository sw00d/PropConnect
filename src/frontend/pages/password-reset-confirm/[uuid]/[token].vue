<template>
  <AuthContentContainer :image="passwordImage">
    <h1>Enter a New Password</h1>
    <p class="text-medium-emphasis mt-2">Let's change your password!</p>

    <VForm @submit.prevent="submit" class="mt-7">
      <div class="mt-1">
        <label class="label text-grey-darken-2" for="password">Password</label>
        <VTextField
          v-model="password"
          prepend-inner-icon="fluent:password-20-regular"
          type="password"
          id="password"
          name="password"
          :error-messages="errors.password"
          :error="!!errors.password"
        />
      </div>
      <div class="mt-5">
        <VBtn
          type="submit"
          block
          min-height="44px"
          color="primary"
          :loading="loading"
        >
          Update Password
        </VBtn>
      </div>
    </VForm>
    <p class="text-body-2 mt-10">
      <span
      >
        Need something else?
        <NuxtLink to="/signup/user-info" class="font-weight-bold text-primary">
          Sign Up
        </NuxtLink>
        or
        <NuxtLink to="/sign-in" class="font-weight-bold text-primary">
          Sign In
        </NuxtLink>
      </span>
    </p>
  </AuthContentContainer>
</template>

<script setup lang="ts">
// Imports
import passwordImage from "@/assets/signup/password.png"
import AuthContentContainer from "~/components/Containers/AuthContentContainer.vue";
import {useRequest} from "~/composables/useRequest";
import {useRouter} from "#imports";
import {useSnackbarStore} from "~/store/snackbarStore";
import {useRoute} from "#app";

// Data
definePageMeta({
  layout: "signup",
  // middleware: 'guest'
})

const password = ref("");
const errors = ref({});
const loading = ref(false);
// Lifecycle

// Methods
const snackbarStore = useSnackbarStore()
const submit = async () => {
  try {
    errors.value = {}
    loading.value = true
    const route = useRoute()
    const res = await useRequest(`/passwordreset/confirm/${route.params.uuid}/${route.params.token}/`, {
        method: 'POST',
        body: {
          new_password_1: password.value,
          new_password_2: password.value
        }
      })

    if (res.error?.value) {
      if (res.error.value?.data?.new_password_1 || res.error.value?.data?.new_password_2) {
        errors.value = {password: res.error.value.data.new_password_1 || res.error.value?.data?.new_password_2}
      } else {
        throw new Error(res.error.value)
      }
    } else {
      snackbarStore.displaySnackbar('success', 'Password changed. Please sign in.')
      const router = useRouter()
      router.push('/sign-in')
    }
  } catch (e) {
    snackbarStore.displaySnackbar('error', 'Something went wrong. Please try again later.')
  } finally {
    loading.value = false
  }
};
// Hooks
</script>

<style scoped lang="stylus">

</style>
