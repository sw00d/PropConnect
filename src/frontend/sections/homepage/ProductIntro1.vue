<template>
  <div class="bg-primary text-white">
    <div class="content-container d-flex justify-space-between align-center py-10">
      <v-row>
        <v-col>
          <div class="d-flex flex-column justify-center h-100">
            <div class="font-weight-bold font-40">
              Streamlining Tenant Communication
            </div>
            <div class="font-weight-medium opacity-7 font-24 mt-11">
              Take a step back from the constant juggle between tenants, vendors, and landlords. Our solution brings
              efficiency
              to your role by facilitating direct communication between tenant and vendor. With in depth oversight,
              you're
              free
              from mundane tasks, empowering you to focus on expanding your portfolio or simply enjoying your
              well-deserved
              downtime.
            </div>
          </div>
        </v-col>
        <v-col cols="3" class="d-flex justify-end">
          <v-sheet height="415px" width="225px" class="bg-transparent">
            <v-img :src="iphoneOutline"/>
          </v-sheet>
        </v-col>
      </v-row>
    </div>

  </div>
</template>

<script setup lang="ts">
import iphoneOutline from "@/assets/iphoneOutline.png"
// Imports

// Data

// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
