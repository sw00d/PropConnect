<template>
  <v-app class="overflow-hidden">
    <v-main>
      <v-container>

        <v-list-item class="mb-10">
          <div class="d-flex justify-space-between  align-center">
            <NuxtLink to="/">
              <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
            </NuxtLink>
          </div>
        </v-list-item>

        <slot/>
      </v-container>
      <Footer/>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";
import {useUserStore} from "~/store/userStore";
import Footer from "~/sections/homepage/Footer.vue";

const auth = useUserStore()

const {theme, toggle_theme} = useThemeSwitcher()

const logout = async () => {
  try {
    await auth.logout()
  } catch (e) {
    console.error(e)
  }
}

</script>

<style lang="scss" scoped>
.rotate-180 {
  transform: rotate(180deg);
  transition: .2s;
}

.icon {
  transition: .5s;
}
</style>
