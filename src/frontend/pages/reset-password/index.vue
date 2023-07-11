<template>
  <AuthContentContainer :image="apartment">
    <h1>Reset password</h1>
    <p class="text-medium-emphasis mt-2">Add your email to get instructions</p>

    <VForm @submit.prevent="submit" class="mt-7">
      <div class="mt-1">
        <label class="label text-grey-darken-2" for="email">Email</label>
        <VTextField
          :rules="[ruleRequired, ruleEmail]"
          v-model="email"
          prepend-inner-icon="fluent:mail-24-regular"
          id="email"
          name="email"
          type="email"
          :error-messages="errors.email"
          :error="!!errors.email"
        />
      </div>
      <div class="mt-5">
        <VBtn type="submit" block min-height="44px" color="primary" :loading="loading">
          Send instructions
        </VBtn>
      </div>
    </VForm>
    <p class="text-body-2 mt-10">
      <span>
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
import apartment from "@/assets/signup/apartment.png"
import AuthContentContainer from "~/components/Containers/AuthContentContainer.vue";
import {useRequest, useRouter} from "#imports";
import {useSnackbarStore} from "~/store/snackbarStore";

definePageMeta({
  layout: "signup",
  // middleware: 'guest'
})

const email = ref("");
const password = ref("");
const errors = ref({});
const loading = ref(false);
const {ruleEmail, ruleRequired} = useFormRules();

const snackbarStore = useSnackbarStore()
const submit = async () => {
  try {
    errors.value = {}
    loading.value = true
    const res = await useRequest('/passwordreset/', {
      method: 'POST',
      body: {email: email.value}
    })

    if (res.error?.value) {
      if (res.error.value?.data?.email) {
        errors.value = res.error.value.data.email
      } else {
        throw new Error(res.error.value)
      }
    } else {
      snackbarStore.displaySnackbar('success', 'Email sent. Please check your inbox.')
      const router = useRouter()
      router.push('/sign-in')
    }
  } catch (e) {
    snackbarStore.displaySnackbar('error', 'Something went wrong. Please try again later.')
  } finally {
    loading.value = false
  }
};
</script>
