import {useUserStore} from "~/store/userStore";
import {useSnackbarStore} from "~/store/snackbarStore";

export default defineNuxtRouteMiddleware(async (_to, _from) => {
    const csrftoken = useCookie('csrftoken')
    if (!csrftoken.value) {
        csrftoken.value = null
        return navigateTo('/')
    }

    const auth = useUserStore()
    if (!auth.authUser || !auth.isLoggedIn) {
        return navigateTo('/')
    }
    else if (_from.path === '/signup/company-info' && _to.path === '/dashboard') {
        // allows user to go back from signing up
        // await auth.logout()
        return navigateTo('/')
    }
    else if (
        auth.authUser && !auth.authUser.company && _to.path !== '/signup/company-info' && _from.path !== '/signup/company-info'
    ) {
        const snackbar = useSnackbarStore()
        snackbar.displaySnackbar('highlight', "Please provide a company first.")
        return navigateTo('/signup/company-info')
    }
})
