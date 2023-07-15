import {createVuetify} from "vuetify";
import {LIGHT_THEME, light, dark} from "~/utils/themes";
import {defaults} from "~/utils/defaults";

export default defineNuxtPlugin((app) => {
    const vuetify = createVuetify({
        ssr: true,
        defaults,
        // add theme
        theme: {
            defaultTheme: LIGHT_THEME,
            themes: {
                light,
                dark,
            },

            // add color variations
            // variations: {
            //     colors: ["primary", "secondary"],
            //     lighten: 3,
            //     darken: 3,
            // },
        },
        // Add the custom iconset
        icons: {
            defaultSet: "custom",
            sets: {
                custom,
            },
        },
    });

    app.vueApp.use(vuetify);
});
