<template>
    <div class="wrapper">
        <div class="d-flex flex-column">
            <div class="d-flex justify-center w-100">
                <v-container class="d-flex align-center justify-space-between">
                    <div class="d-flex align-center justify-space-between mb-4">
                        <v-sheet class="d-flex align-center mr-4 bg-transparent" max-height="56px">
                            <v-img :src="logoGraphic" width="40px" height="56px"/>
                        </v-sheet>
                        <v-toolbar-title class="lh-38 text-primary font-weight-black d-flex">
                            PropConnect
                        </v-toolbar-title>
                    </div>

                    <nuxt-link :to="store?.isLoggedIn ? '/dashboard' : '/sign-in'">
                        <button
                            class="border-b sign-in font-14 text-primary"
                        >
                            {{ store?.isLoggedIn ? 'Portal' : 'Sign in' }}
                        </button>
                    </nuxt-link>
                </v-container>
            </div>
        </div>

        <v-container class="mt-sm-10">
            <div class="d-flex justify-space-between align-center">
                <div class="text-h3 text-sm-h2 font-weight-black lh-70">
                    Maintenance Coordination
                    <br>
                    Made Easy
                </div>
                <v-sheet width="250px" height="250px" class="bg-transparent hidden-xs">
                    <v-img
                        transition="slide-x-reverse-transition"
                        :src="robotSVG"
                    />
                </v-sheet>
            </div>

            <div class="d-flex justify-space-between flex-column flex-md-row mt-5">
                <div class="text-h6 opacity-5 ls-0 mr-10">
                    Leverage <i><b>AI-driven</b></i> innovation to seamlessly match tenant concerns with <i><b>optimal
                    solutions</b></i>.
                </div>

                <v-btn
                    variant="flat"
                    width="250px"
                    height="50px"
                    class="font-weight-black bg-primary font-20 mt-10"
                    to="/signup/user-info"
                >
                    Get Started
                </v-btn>
            </div>
        </v-container>
    </div>
</template>

<script setup lang="ts">
// Imports
import robotSVG from "assets/public-site/robotSVG.svg"
import {useUserStore} from "~/store/userStore";
import logoGraphic from "assets/logos/logo-graphic-only.png";

// Data
const store = useUserStore()
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">
.wrapper {
    padding-bottom: 100px
    background: radial-gradient(circle, #fcfcfc, #cae0ee);
}

.sign-in {
    height: 18px;
    border-color: var(--v-theme-primary) !important;
}
</style>
