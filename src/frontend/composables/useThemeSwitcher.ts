import {ref, onMounted} from 'vue'
import {useAuth} from "~/composables/useAuth";
import {useTheme} from "vuetify";

export function useThemeSwitcher() {
    const theme = useTheme()

    const setThemeFromLocalStorage = () => {
        if (theme) {
            const isDark = localStorage.getItem("isDark");
            theme.global.name.value = isDark === 'true' ? 'dark' : 'light'
        }
    };
    const toggle_theme = (init?: boolean) => {
        theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
        // save to localstorage
        localStorage.setItem("isDark", JSON.stringify(theme.global.current.value.dark));
    }

    onMounted(setThemeFromLocalStorage);

    return {
        toggle_theme,
        theme,
    }
}
