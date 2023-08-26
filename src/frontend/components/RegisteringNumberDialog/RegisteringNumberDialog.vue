<template>
    <v-dialog
        :modelValue="modelValue"
        width="500px"
        max-width="90%"
        :persistent="!user.hasActiveSubscription"
    >
        <v-card>
            <v-card-text class="d-flex align-center flex-column">
                <div class="d-flex align-center my-4">
                    <v-sheet class="d-flex align-center mr-4 bg-transparent">
                        <v-img :src="logoGraphic" width="40px"/>
                    </v-sheet>
                    <v-toolbar-title class="lh-38 text-primary font-weight-black d-flex">
                        PropConnect
                    </v-toolbar-title>
                </div>
                <div class="text-primary font-20 weight-700 my-5">
                    Thanks for joining! 🎉
                </div>
                <div class="font-14 text-black mt-4 text-center">
                    We are in the process of setting up your dedicated hotline. While it typically takes a few business
                    days, rest assured you'll be notified via email once your number is primed for use.
                    <br>
                    <br>
                    <i>
                        Note: Your trial will commence only after the setup is finalized.
                    </i>
                </div>

                <v-btn
                    variant="flat"
                    width="200px"
                    height="40px"
                    class="font-weight-black bg-primary font-14 mt-10 mb-4"
                    to="/"
                >
                    Back to site
                </v-btn>

            </v-card-text>

        </v-card>

    </v-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useUserStore } from "~/store/userStore"
import logoGraphic from "assets/logos/logo-graphic-only.png"

const config = useRuntimeConfig()
const auth = useUserStore()

// Define props and emits
const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['input'])

const loading = ref(false)
const user = useUserStore()


watch(
    () => user.hasActiveSubscription,
    (val) => {
        // This handles a slow server response and just closes the dialog if the user does indeed have a subscription
        if (val) {
            emit('input', false)
        }
    }
)

</script>

<style scope lang="stylus">
.subscription-box {
    padding: 14px
    border: 1px solid #000
    border-radius: 10px;
    box-shadow: 4px 4px 20px 0px rgba(0, 0, 0, 0.25);
}
</style>
