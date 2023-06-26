<template>
  <AuthContentContainer :image="beachHouse">
    <template #default>
      <div>

        <div class="text-h4 font-weight-black text-primary">Welcome Sam!</div>
        <div class="mb-6 mt-2">
          Let's hear a bit about your company!
        </div>

        <v-form>
          <v-text-field
            v-model="companyName"
            placeholder="Company Name"
          />
          <v-text-field
            v-model="website"
            placeholder="Company Name"
          />

          <v-select
            v-model="numberOfDoors"
            placeholder="How many doors will we manage for you?"
            :items="[1,2,3]"
          />

          <v-btn
            color="primary"
            type="submit"
            to="/dashboard"
            width="100%"
          >
            Continue
          </v-btn>
        </v-form>
      </div>
    </template>
  </AuthContentContainer>
</template>

<script setup lang="ts">
// Imports
import beachHouse from "@/assets/signup/beach-house.png"
import AuthContentContainer from "~/components/Signup/AuthContentContainer.vue";

// Data
const companyName = ref('')
const website = ref('')
const numberOfDoors = ref(1)
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
