<template>
  <div>
    <NuxtLayout>
      <NuxtPage/>
    </NuxtLayout>
    <SnackbarComponent />
  </div>
</template>
<script setup lang="ts">
import SnackbarComponent from "~/components/Snackbar/SnackbarComponent.vue";
import {useUserStore} from "~/store/userStore";
// Imports

// Data
const user = useUserStore()

// Lifecycle
onMounted(()=>{
    user.fetchUser()
})
// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
