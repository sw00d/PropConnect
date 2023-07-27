<template>
    <AuthContentContainer :image="signup">
        <template #default>
            <div class="text-h4 font-weight-black text-primary">Welcome to PropConnect</div>
            <div class="mb-6 mt-2">
                Let's start with the basics. 😃
            </div>
            <v-form :model-value="valid" @submit.prevent="onSubmit">
                <v-row class="d-flex" no-gutters>
                    <v-col cols="6">
                        <v-text-field
                            v-model="firstName"
                            :rules="nameRules"
                            :error-messages="errors.first_name"
                            :error="errors.first_name"
                            placeholder="First name"
                            class="mr-4"
                        />
                    </v-col>
                    <v-col cols="6">
                        <v-text-field
                            v-model="lastName"
                            :rules="nameRules"
                            :error-messages="errors.last_name"
                            :error="errors.last_name"
                            placeholder="Last name"
                        />
                    </v-col>
                </v-row>

                <v-text-field
                    v-model="email"
                    :rules="emailRules"
                    :error-messages="errors.email"
                    :error="errors.email"
                    placeholder="Email"
                    name="email"
                    class="mt-1"
                />
                <v-text-field
                    v-model="password"
                    :rules="passwordRules"
                    :error-messages="errors.password"
                    :error="errors.password"
                    placeholder="Password"
                    type="password"
                    class="mt-1"
                />
                <v-btn
                    type="submit"
                    color="primary"
                    min-height="44px"
                    width="100%"
                    :loading="submitting"
                    :disabled="!valid"
                >
                    Sign Up
                </v-btn>
                <v-checkbox
                    v-model="agreeToTerms"
                    class="mt-1 font-14"
                >
                    <template #label>
                        <div class="font-14">
                            I agree to the terms of service and privacy policy
                        </div>
                    </template>
                </v-checkbox>
                <div class="mt-4 opacity-7 font-12 d-flex align-center">
                    <nuxt-link
                        to="/terms-of-service"
                        class="text-decoration-underline"
                    >
                        Terms of Service
                    </nuxt-link>
                    <div class="mx-3">|</div>
                    <nuxt-link
                        to="/privacy-policy" class="text-decoration-underline">
                        Privacy Policy
                    </nuxt-link>
                </div>
            </v-form>
        </template>

    </AuthContentContainer>
</template>

<script setup lang="ts">
// Imports
import signup from "@/assets/signup/signup.png"
import AuthContentContainer from "~/components/Containers/AuthContentContainer.vue";
import {useUserStore} from "~/store/userStore";
import {useSnackbarStore} from "~/store/snackbarStore";

const router = useRouter();
const auth = useUserStore()

const firstName = ref<string>('');
const lastName = ref<string>('');
const email = ref<string>('');
const password = ref<string>('');
const agreeToTerms = ref<boolean>(false);
const errors = ref({});
const submitting = ref<boolean>(false);

const nameRules = [
    (v: string) => !!v || 'Name is required',
    (v: string) => (v && v.length <= 10) || 'Name must be less than 10 characters'
];

const emailRules = [
    (v: string) => !!v || 'Email is required',
    (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
];

const agreeToTermsRules = [
    (v: boolean) => v || 'Required',
];
const passwordRules = [
    (v: string) => !!v || 'Password is required',
    // (v: string) => (v && v.length >= 8) || 'Password must be at least 8 characters'
];

const valid = computed(() => {
    return firstName.value && lastName.value && email.value && password.value &&
        nameRules.every(rule => rule(firstName.value) === true) &&
        nameRules.every(rule => rule(lastName.value) === true) &&
        emailRules.every(rule => rule(email.value) === true) &&
        passwordRules.every(rule => rule(password.value) === true) &&
        agreeToTermsRules.every(rule => rule(agreeToTerms.value) === true)
});

const onSubmit = async () => {
    if (!valid.value) return
    else {
        // Sign up user and logs them in
        submitting.value = true
        errors.value = {}
        const res = await auth.createUser({
            first_name: firstName.value,
            last_name: lastName.value,
            email: email.value,
            password: password.value,
            agreeToTerms: agreeToTerms.value,
        })

        submitting.value = false

        if (res.error?.value) {
            errors.value = res.error.value.data
            if (res.error.value.statusCode !== 400) {
                const snackbar = useSnackbarStore()
                snackbar.displaySnackbar('error', "Error signing up. Please try again later.")
            }
        } else {
            router.push('/signup/company-info')
        }

    }
    // Submit form here
}
// Hooks
</script>

<style scoped lang="stylus">

</style>
