<template>
  <div class="d-md-flex text-left flex-column justify-center align-center">
    <div class="text-h2 font-weight-black text-left fill-width">Welcome, Master Alex</div>
    <v-row class="fill-width mt-10">
      <v-col>
       <DashboardTable />
      </v-col>
<!--      <v-col cols="2">-->
<!--        <div class="bg-blue w-100 h-100 rounded-xl text-center">-->
<!--          Click on a row to see the details-->
<!--        </div>-->
<!--      </v-col>-->
    </v-row>
  </div>
</template>

<script setup>
import { useDisplay } from 'vuetify'
import DashboardTable from "../components/DashboardTable/DashboardTable"

definePageMeta({
  middleware: ["auth"]
})

const display = ref(useDisplay())


</script>

<style lang="scss" scoped>
.v-data-table-footer {
  display: none !important;
}
</style>
