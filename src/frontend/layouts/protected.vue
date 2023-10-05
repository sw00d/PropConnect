<template>
    <v-layout>
        <ScreenSwitcher>
            <template #forDesktop>
                <PortalNavigationDrawer/>
            </template>
            <template #forMobile>
                <PortalMobileHeader/>
            </template>
        </ScreenSwitcher>
        <v-main style="min-height: 100vh">
<!--            <SubscriptionDialog-->
<!--                :model-value="showSubscriptionDialog"-->
<!--                @input="showSubscriptionDialog=$event"-->
<!--            />-->
            <RegisteringNumberDialog
                :model-value="showRegisteringDialog"
                @input="showRegisteringDialog=$event"
            />
            <slot/>
        </v-main>
    </v-layout>

</template>

<script setup lang="ts">
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";
import {useUserStore} from "~/store/userStore";
import {useRoute} from "vue-router";
import PortalNavigationDrawer from "~/components/Layout/PortalNavigationDrawer.vue";
import ScreenSwitcher from "~/components/ScreenSwitcher/ScreenSwitcher.vue";
import PortalMobileHeader from "~/components/Layout/PortalMobileHeader.vue";
import RegisteringNumberDialog from "~/components/RegisteringNumberDialog/RegisteringNumberDialog.vue";

const auth = useUserStore()
const route = useRoute()

useThemeSwitcher()
const showSubscriptionDialog = ref(false)
const showRegisteringDialog = ref(true)

watch(() => route.path, () => {
    handleSubscriptionCheck()
})
onMounted(() => {
    handleSubscriptionCheck()
})
const handleSubscriptionCheck = () => {
    setTimeout(() => {
        if (!auth.hasActiveSubscription) {
            showSubscriptionDialog.value = true
        } else if (!auth.authUser?.company?.assistant_phone_is_verified){
            showRegisteringDialog.value = true
        }
    }, 1500)
}
</script>

<style lang="stylus" scoped>
.v-main
    background: url("assets/grid_light.svg") 0 0 repeat;

</style>
