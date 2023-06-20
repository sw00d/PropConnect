<template>
  <v-app class="overflow-hidden">
    <v-main>
      <v-container fluid class="h-100">
        <div class="z-index-2 d-flex justify-space-between px-4 pb-4 relative">
          <v-btn
            icon
            variant="outlined"
            class="transition"
            @click="toggle_theme"
          >
            <v-icon
              :class="theme.global.current.value.dark ? 'rotate-180 icon' : ' icon'"
              icon="mdi-theme-light-dark"
              size="30px"
            />
          </v-btn>

          test {{ auth.isLoggedIn }}

          <v-btn
            v-if="auth.isLoggedIn"
            icon
            variant="outlined"
            class="transition ml-4 ml-sm-0"
            @click="logout"
          >
            <v-icon
              class="rotate-180"
              icon="mdi-logout"
              size="24px"
            />
          </v-btn>
        </div>
        <v-row no-gutters justify="center" class="fill-height z-index-1 relative">
          <v-col cols="12" md="10" lg="8" sm="10">
            <slot/>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import {useAuth} from "~/composables/useAuth";
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";

const auth = useAuth()

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
