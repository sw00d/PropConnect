<template>
  <AuthContentContainer :image="signup">
    <template #default>
      <div class="text-h4 font-weight-black text-primary">Welcome to PropConnect</div>
      <div class="mb-6 mt-2">
        Let's start with the basic. 😃
      </div>
      <v-form>
        <div class="d-flex">
          <v-text-field
            v-model="firstName"
            placeholder="First name"
            class="mr-4"
          />
          <v-text-field
            v-model="lastName"
            placeholder="Last name"
          />
        </div>
        <v-text-field
          v-model="email"
          placeholder="Email"
        />
        <v-text-field
          v-model="password"
          placeholder="Password"
        />
        <v-btn
          color="primary"
          type="submit"
          to="/signup/company-info"
          width="100%"
        >
          Sign Up
        </v-btn>
      </v-form>
    </template>

  </AuthContentContainer>
</template>

<script setup lang="ts">
// Imports
import signup from "@/assets/signup/signup.png"
import AuthContentContainer from "~/components/Signup/AuthContentContainer.vue";

// Data
const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
