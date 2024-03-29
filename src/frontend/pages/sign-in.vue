<template>
  <AuthContentContainer :image="apartment">
    <template #default>
      <div class="text-h4 font-weight-black text-primary">Sign in</div>
      <div class="mb-6 mt-2">
        Welcome back! Let's get started
      </div>
      <v-form @submit.prevent="submit" ref="form" class="mt-7">
        <div class="mt-1">
          <label class="label text-grey-darken-2" for="email">Email</label>
          <v-text-field
            :rules="[ruleRequired, ruleEmail]"
            v-model="email"
            prepend-inner-icon="fluent:mail-24-regular"
            id="email"
            name="email"
            type="email"
            :error-messages="errors.email"
            :error="!!errors.email"
          ></v-text-field>
        </div>
        <div class="mt-1">
          <label class="label text-grey-darken-2" for="password">Password</label>
          <v-text-field
            :rules="[ruleRequired, rulePassLen]"
            v-model="password"
            prepend-inner-icon="fluent:password-20-regular"
            id="password"
            name="password"
            type="password"
            :error-messages="errors.password"
            :error="!!errors.password"
          ></v-text-field>
        </div>
        <div class="mt-5">

          <v-btn
            type="submit"
            color="primary"
            min-height="44px"
            :loading="isLoading"
            width="100%"
          >
            Sign In
          </v-btn>
        </div>
      </v-form>
      <p class="text-body-2 mt-10">
        <nuxt-link to="/reset-password" class="font-weight-bold text-primary"
        >
          Forgot password?
        </nuxt-link>
      </p>
      <p class="text-body-2 mt-4">
        <span>
          Don't have an account?
          <nuxt-link to="/signup/user-info" class="font-weight-bold text-primary">
            Sign Up
          </nuxt-link>
        </span>
      </p>
    </template>
  </AuthContentContainer>
</template>

<script setup>
import apartment from "@/assets/signup/apartment.png"
import AuthContentContainer from "../components/Containers/AuthContentContainer"
import { useSnackbarStore } from "../store/snackbarStore"
import { useUserStore } from "../store/userStore"

definePageMeta({
  layout: "signup",
  // middleware: 'guest'
})

const { ruleEmail, rulePassLen, ruleRequired } = useFormRules()
const { login } = useUserStore()

const email = ref("")
const password = ref("")
const isLoading = ref(false)
const errors = ref({})
const form = ref(null)
const snackbarStore = useSnackbarStore()


const submit = async () => {
  const { valid } = await form.value.validate()
  if (valid || true) {

    isLoading.value = true // Set isLoading to true when submitting
    errors.value = {} // Reset errors

    const { error, data } = await login(email.value, password.value)

    if (error.value) {
      isLoading.value = false // Set isLoading to false if there's an error
      errors.value = error.value.data
      const display_error = error.value.data.non_field_errors?.[0]
      snackbarStore.displaySnackbar('error', display_error || 'Error Occurred')
    } else {
      navigateTo("/dashboard")
    }
    isLoading.value = false // Set isLoading to false after the request is completed
  }
}

</script>

<style scoped lang="stylus">
.wrapper {
  min-height: 100vh;
  min-width: 100vw;
  background: url("assets/grid_light.svg") 0 0 repeat;
}

</style>
