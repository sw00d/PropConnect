<template>
  <v-app class="overflow-hidden">
    <v-main>
      <v-container fluid class="fill-height">
        <div class="z-index-2 d-flex justify-space-between fill-width px-4 ">
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
          <v-sheet class="bg-transparent hidden-sm-and-up relative" width="150px" height="150px">
            <div class="top-gradient"></div>
                <div class="bottom-gradient"></div>
                <div class="left-gradient"></div>
                <div class="right-gradient"></div>
                <v-img :src="logo_img" alt="description" class="opacity-3"/>
          </v-sheet>
        </div>
        <v-row no-gutters justify="center" class="fill-height z-index-1 relative">
          <v-col cols="12" md="10" lg="8" sm="10">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="12" sm="6">
                <slot/>
              </v-col>
              <v-col class="hidden-sm-and-down fill-height d-flex justify-center align-center relative pl-5" md="6">
                <div class="top-gradient"></div>
                <div class="bottom-gradient"></div>
                <div class="left-gradient"></div>
                <div class="right-gradient"></div>
                <v-img :src="logo_img" alt="description" class=""/>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import logo_img from "~/assets/wrench.png";
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";

const {theme, toggle_theme} = useThemeSwitcher()
</script>

<style lang="scss" scoped>

//.top-gradient {
//  z-index: 1;
//  background: linear-gradient(to bottom, rgb(var(--v-theme-background)), transparent);
//  position: absolute;
//  top: 0;
//  height: 100px;
//  width: 100%;
//}
//.bottom-gradient {
//  z-index: 1;
//  background: linear-gradient(to top, rgb(var(--v-theme-background)), transparent);
//  position: absolute;
//  bottom: 0;
//  height: 100px;
//  width: 100%;
//}
//
//.right-gradient {
//  z-index: 1;
//  background: linear-gradient(to left, rgb(var(--v-theme-background)), transparent);
//  position: absolute;
//  right: 0;
//  height: 100%;
//  width: 100px;
//}
//
//.left-gradient {
//  z-index: 1;
//  background: linear-gradient(to right, rgb(var(--v-theme-background)), transparent);
//  position: absolute;
//  left: 0;
//  height: 100%;
//  width: 100px;
//}

.rotate-180 {
  transform: rotate(180deg);
  transition: .2s;
}

.icon {
  transition: .5s;
}


</style>
