// @ts-nocheck
import vuetify from "vite-plugin-vuetify";

// PWA Config
const title = "PropConnect";
const shortTitle = "PropConnect";
const description = "PropConnect -- Your new AI Maintenance Coordinator.";
const image = "https://propconnect.io/seo-logo.png";
const url = "https://propconnect.io";

// https://v3.nuxtjs.org/api/configuration/nuxt.config
export default defineNuxtConfig({
    // Runtime Config
    runtimeConfig: {
        public: {
            server_url: process.env.API_BASE_URL || 'http://localhost:8000/api',
            DEFAULT_TWILIO_NUMBER: process.env.DEFAULT_TWILIO_NUMBER,
            STRIPE_PUBLISHABLE_KEY: process.env.STRIPE_PUBLISHABLE_KEY,
        },
    },

    // import styles
    css: ["@/assets/main.scss", "@/assets/stylus/index.styl"],
    // enable takeover mode
    typescript: {shim: false},
    build: {transpile: ["vuetify"]},
    pinia: {
        autoImports: [
            // automatically imports `defineStore`
            'defineStore', // import { defineStore } from 'pinia'
            ['defineStore', 'definePiniaStore'], // import { defineStore as definePiniaStore } from 'pinia'
        ],
    },
    piniaPersistedstate: {
        storage: 'localStorage'
    },
    modules: [
        '@pinia/nuxt',
        '@vueuse/nuxt',
        '@pinia-plugin-persistedstate/nuxt',

        // Vuetify
        async (options, nuxt) => {
            nuxt.hooks.hook("vite:extendConfig", (config) =>
                // @ts-ignore
                config.plugins.push(vuetify())
            );
        },
    ],
    vite: {
        server: {
            watch: {usePolling: true}
        },

        // Make styles load properly in production TODO: Fix this!
        build: {
            rollupOptions: {
                treeshake: false,
            }
        }
    },

    app: {
        head: {
            title: "PropConnect",
            titleTemplate: "%s | PropConnect",
            link: [
                {rel: "stylesheet", href: "https://rsms.me/inter/inter.css"},
                {rel: "preconnect", href: "https://rsms.me/"},
                {rel: "icon", type: "image/x-icon", href: "/favicon.ico"},
                {rel: "canonical", href: url},
                {rel: "preconnect", href: "https://fonts.googleapis.com"},
                {rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: true},
                {
                    rel: "stylesheet",
                    href: "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap"
                },
            ],
            meta: [
                {
                    hid: "description",
                    name: "description",
                    content: description,
                },
                {property: "og:site_name", content: title},
                {hid: "og:type", property: "og:type", content: "website"},
                {
                    hid: "og:url",
                    property: "og:url",
                    content: url,
                },
                {
                    hid: "og:image:secure_url",
                    property: "og:image:secure_url",
                    content: image,
                },
                {
                    hid: "og:title",
                    property: "og:title",
                    content: title,
                },
                {
                    hid: "og:description",
                    property: "og:description",
                    content: description,
                },
                {
                    hid: "og:image",
                    property: "og:image",
                    content: image,
                },
                //Twitter
                {name: "twitter:card", content: "summary_large_image"},
                {
                    hid: "twitter:url",
                    name: "twitter:url",
                    content: url,
                },
                {
                    hid: "twitter:title",
                    name: "twitter:title",
                    content: title,
                },
                {
                    hid: "twitter:description",
                    name: "twitter:description",
                    content: description,
                },
                {
                    hid: "twitter:image",
                    name: "twitter:image",
                    content: image,
                },
            ],
        },
    }
});
