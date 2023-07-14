<template>
  <v-app class="overflow-hidden">
    <v-main>
      <v-container fluid class="h-100">
        <v-row no-gutters justify="center" class="fill-height z-index-1 relative">
          <v-col cols="12" md="10" lg="8" sm="10">

            <v-list-item class="mb-10">
              <div class="d-flex justify-space-between  align-center">
                <NuxtLink to="/">
                  <v-toolbar-title class="lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
                </NuxtLink>
              </div>
            </v-list-item>

            <slot/>
          </v-col>
        </v-row>
      </v-container>
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
