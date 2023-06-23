<template>
  <v-app class="overflow-hidden bg-white">
    <v-app-bar class="bg-transparent">
      <div class="d-flex justify-center w-100">
        <div class="content-container d-flex align-center">
          <v-toolbar-title class="font-30 lh-38 text-primary font-weight-black">PropConnect</v-toolbar-title>
          <v-spacer></v-spacer>
          <button
            class="border-b sign-in font-14 text-primary"
            @click="logout"
          >
            Sign in
          </button>
        </div>
      </div>
    </v-app-bar>
    <v-main>
      <div class="content-container">
        <!--        <v-btn-->
        <!--          icon-->
        <!--          variant="outlined"-->
        <!--          class="transition z-index-1"-->
        <!--          @click="toggle_theme"-->
        <!--        >-->
        <!--          <v-icon-->
        <!--            :class="theme.global.current.value.dark ? 'rotate-180 icon' : ' icon'"-->
        <!--            icon="mdi-theme-light-dark"-->
        <!--            size="30px"-->
        <!--          />-->
        <!--        </v-btn>-->
        <slot/>
      </div>
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

<style lang="stylus" scoped>
.rotate-180 {
  transform: rotate(180deg);
  transition: .2s;
}

.icon {
  transition: .5s;
}

.sign-in {
  height: 18px;
  border-color: var(--v-theme-primary) !important;
}

.v-main {
  .content-container {
    margin-top: 100px;
  }
}
//>>> .v-toolbar {
//  background transparent;
//}
</style>
