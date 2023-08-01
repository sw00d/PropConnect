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
            <ReleasingSoonDialog
                :model-value="showSubscriptionDialog"
                @input="showSubscriptionDialog=$event"
            />
            <slot/>
        </v-main>
    </v-layout>

</template>

<script setup lang="ts">
import {useThemeSwitcher} from "~/composables/useThemeSwitcher";
import {useUserStore} from "~/store/userStore";
import {useRoute} from "vue-router";
import SubscriptionDialog from "~/sections/portal/subscription-dialog/SubscriptionDialog.vue";
import PortalNavigationDrawer from "~/components/Layout/PortalNavigationDrawer.vue";
import ScreenSwitcher from "~/components/ScreenSwitcher/ScreenSwitcher.vue";
import PortalMobileHeader from "~/components/Layout/PortalMobileHeader.vue";
import ReleasingSoonDialog from "~/sections/portal/ReleasingSoonDialog/ReleasingSoonDialog.vue";

const user = useUserStore()
const route = useRoute()

useThemeSwitcher()
const showSubscriptionDialog = ref(false)

watch(() => route.path, () => {
    handleSubscriptionCheck()
})
onMounted(() => {
    handleSubscriptionCheck()
})
const handleSubscriptionCheck = () => {
    setTimeout(() => {
        if (!user.hasActiveSubscription) {
            showSubscriptionDialog.value = true
        }
    }, 1500)
}
</script>

<style lang="stylus" scoped>
.v-main
    background: url("assets/grid_light.svg") 0 0 repeat;

</style>
