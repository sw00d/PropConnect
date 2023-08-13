<template>
    <div class="text-center">
        <v-dialog
            :modelValue="modelValue"
            width="400px"
            max-width="90%"
            :persistent="!user.hasActiveSubscription"
        >
            <v-card>
                <v-chip color="success" class="font-weight-bold absolute top right mt-2 mr-2" variant="flat"
                        size="small">
                    ✨ Beta
                </v-chip>
                <v-card-text>
                    <v-toolbar-title class="lh-38 text-primary font-30 font-weight-black">PropConnect</v-toolbar-title>
                    <div class="font-14 text-black">
                        Small cost. Large benefit. Enjoy a 7 day free trial!
                    </div>

                    <div class="subscription-box mt-5 relative">
                        <div class="d-flex justify-space-between">
                            <v-toolbar-title class="text-primary font-30 font-weight-black">
                                $12
                                <span class="font-14 opacity-5 text-black font-weight-medium">/month</span>
                            </v-toolbar-title>
                            <v-chip
                                color="secondary"
                                variant="flat"
                                class="font-weight-bold trial-chip px-7"
                            >
                                <span class="text-primary">
                                    Free Trial
                                </span>
                            </v-chip>
                        </div>

                        <div class="font-12 opacity-5 text-black ls-0 mt-3 font-weight-medium pr-10">
                            $12.00 + $0.70 for every conversation that's managed by our system.
                        </div>
                    </div>


                    <div class="mt-8 card-container">
                        <div class="d-flex justify-space-between mb-3">
                            <div class="font-weight-bold">
                                Credit Card:
                            </div>
                            <div class="d-flex">
                                <v-img
                                    :src="visa"
                                    width="33px"
                                    height="22px"
                                    class="mr-1"
                                    alt="credit card logo"
                                />
                                <v-img
                                    :src="mastercard"
                                    width="33px"
                                    height="22px"
                                    class="mr-1"
                                    alt="credit card logo"
                                />
                                <v-img
                                    :src="discover"
                                    width="33px"
                                    height="22px"
                                    class="mr-1"
                                    alt="credit card logo"
                                />
                                <v-img
                                    :src="amex"
                                    width="33px"
                                    height="22px"
                                    class="mr-1"
                                    alt="credit card logo"
                                />
                            </div>
                        </div>

                        <div ref="cardNumRef"/>
                        <div class="d-flex mt-2">
                            <div ref="cardExpiryRef" class="card-exp mr-2"/>
                            <div ref="cardCvcRef" class="cvc"/>
                        </div>

                        <div class="font-12 text-error mt-2">
                            {{ cardError }}
                        </div>
                    </div>
                    <div class="font-12 text-black opacity-8">
                        You can enjoy a 7 day free trial. After that, you will be charged $12.00 per month.
                    </div>

                    <v-btn
                        variant="flat"
                        width="100%"
                        height="48px"
                        class="font-weight-black bg-primary font-18 mt-10 mb-4"
                        @click="submit"
                        :loading="loading"
                    >
                        Start trial
                    </v-btn>
                </v-card-text>

            </v-card>

        </v-dialog>
    </div>
</template>

<script setup>
import amex from '@/assets/portal/misc/amex.png'
import mastercard from '@/assets/portal/misc/mastercard.png'
import visa from '@/assets/portal/misc/visa.png'
import discover from '@/assets/portal/misc/discover.png'

import { ref, watch, onMounted } from 'vue'
import { loadStripe } from '@stripe/stripe-js'
import { useUserStore } from "~/store/userStore"
import { useRequest } from "~/composables/useRequest"
import { useCompanyStore } from "~/store/compayStore"
import { useSnackbarStore } from "~/store/snackbarStore"

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
const cardNumRef = ref(null)
const cardExpiryRef = ref(null)
const cardCvcRef = ref(null)
const stripe = ref(null)
const user = useUserStore()
const cardError = ref('')

// create stripe elements
let cardNumber, cardExpiry, cardCvc

const elementStyles = {
    base: {
        color: '#32325D',
        fontWeight: 500,
        fontSize: '16px',
        fontSmoothing: 'antialiased',
    },
    invalid: {
        color: '#E25950',

        '::placeholder': {
            color: '#FFCCA5',
        },
    },
}

const elementClasses = {
    focus: 'focused',
    empty: 'empty',
    invalid: 'invalid',
}

watch(
    () => user.hasActiveSubscription,
    (val) => {
        // This handles a slow server response and just closes the dialog if the user does indeed have a subscription
        if (val) {
            emit('input', false)
        }
    }
)

const init = async () => {
    stripe.value = await loadStripe(config.public.STRIPE_PUBLISHABLE_KEY)
    const elements = stripe.value.elements()

    cardNumber = elements.create('cardNumber', {
        style: elementStyles,
        classes: elementClasses,
    })
    cardNumber.mount(cardNumRef.value)

    cardExpiry = elements.create('cardExpiry', {
        style: elementStyles,
        classes: elementClasses,
    })
    cardExpiry.mount(cardExpiryRef.value)

    cardCvc = elements.create('cardCvc', {
        style: elementStyles,
        classes: elementClasses,
    })
    cardCvc.mount(cardCvcRef.value)
}
onMounted(() => init())

watch(() => props.modelValue, (val) => {
    if (val) {
        init()
    }
})

const submit = async () => {
    try {
        loading.value = true
        cardError.value = ''

        const payload = {
            card: cardNumber,
            billing_details: {
                email: user.authUser.email,
            }
        }

        const result = await stripe.value.createPaymentMethod({
            card: payload.card,
            type: 'card',
        })

        if (result.error) {
            cardError.value = result.error?.message || 'Error Occurred'
            throw(result.error)
        }

        const updateRes = await useRequest(`/companies/${ user.authUser.company.id }/`, {
            method: "PATCH",
            body: { payment_method_id: result.paymentMethod?.id },
        })
        if (updateRes.error?.value) {
            cardError.value = 'Error Occurred. Please clear cache and try again.'
            throw new Error(updateRes.error)
        }

        const finalizeSignupRes = await useRequest(`companies/${ user.authUser.company.id }/finalize_signup/`, {
            method: 'POST',
            payment_method_id: result.paymentMethod?.id,
        })

        if (finalizeSignupRes.error?.value) {
            cardError.value = 'Error Occurred. Please clear your cache and try again.'
            throw new Error(finalizeSignupRes.error)
        }

        window.location.reload()
    } catch (e) {
        console.error(e)
        if (e.message) {
            const snackbar = useSnackbarStore()
            snackbar.displaySnackbar('error', "Error occurred")
        }
        loading.value = false
    }
    loading.value = false

}

</script>

<style scope lang="stylus">
.subscription-box {
    padding: 14px
    border: 1px solid #000
    border-radius: 10px;
    box-shadow: 4px 4px 20px 0 rgba(0, 0, 0, 0.25);
}

.trial-chip {
    box-shadow: 4px 4px 20px 0 rgba(0, 0, 0, 0.25);
    border-radius: 10px !important;

}

.card-container
    >>> .card-exp
        flex: 30%

    >>> .cvc
        flex 1

.StripeElement
    background white
    padding 17px 12px
    border 1px solid rgba(0, 0, 0, 0.3)
    border-radius 4px
    transition .2s
    width: 100%;

    &:hover
        border 1px solid rgba(0, 0, 0, 0.5)
</style>
