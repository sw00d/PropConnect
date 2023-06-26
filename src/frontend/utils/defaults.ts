import { DefaultsInstance } from "vuetify/lib/framework.mjs";

/**
 * A few defaults that I like
 */
export const defaults: DefaultsInstance = {
	VAppBar: {
		elevation: 0,
	},
	VBtn: {
		variant: "flat",
		height: 38,
		rounded: "lg",
		size: "small",
        class: 'font-16'
	},
	VTextField: {
		color: "primary",
		variant: "outlined",
		density: "comfortable",
	},
    VSelect: {
		color: "primary",
		variant: "outlined",
		density: "comfortable",
	},
};
