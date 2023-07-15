import {useUserStore} from "~/store/userStore";

export default defineNuxtRouteMiddleware(async (_to, _from) => {
    // unused still but should mostly likely work
    const csrftoken = useCookie('csrftoken')
    const sessionid = useCookie('sessionid')
    // console.log('csrftoken', csrftoken.value)
    if (csrftoken.value || sessionid.value) {
        return navigateTo('/dashboard')
    }
})
