import {ThemeDefinition} from "vuetify";

// String that represents the name of the theme I am using
export const LIGHT_THEME = "light";
// Light mode theme
export const light: ThemeDefinition = {
    dark: false,
    colors: {
        highContrast: ckcColors.black,
        background: ckcColors.gray[200],
        surface: "#FFFFFF",
        surfaceSecondary: ckcColors.slate[500],
        primary: "#000080",
        secondary: "#8CD1FD",
        highlight: "#FF7F00",
        error: ckcColors.red[500],
        info: ckcColors.blue[500],
        success: ckcColors.green[900],
        warning: ckcColors.amber[500],
    },
};

// String that represents the name of the dark theme I am using
export const DARK_THEME = "dark";
// Dark mode theme
export const dark: ThemeDefinition = {
    dark: true,
    colors: {
        highContrast: ckcColors.white,
        background: ckcColors.gray[800],
        surface: ckcColors.slate[900],
        surfaceSecondary: ckcColors.slate[700],
        primary: ckcColors.purple[600],
        secondary: ckcColors.sky[600],
        error: ckcColors.red[500],
        info: ckcColors.blue[500],
        success: ckcColors.green[900],
        warning: ckcColors.amber[500],
    },
};
