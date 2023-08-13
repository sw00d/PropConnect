// @ts-nocheck
import {defineStore} from 'pinia';
import {UserT, UserWithoutPasswordT} from '~/types/authTypes'
import {useRequest} from '~/composables/useRequest'
import {navigateTo} from "#app";

export const useUserStore = defineStore('user', {
    persist: true,
    id: 'user',
    state: () => ({
        authUser: null,
        isLoggedIn: false
    }),
    getters:{
        hasActiveSubscription(): boolean {
            return this.authUser?.company?.current_subscription?.status === 'active' || this.authUser?.company?.current_subscription?.status === 'trialing'
        }
    },
    actions: {
        setUser(user: UserT | UserWithoutPasswordT | null) {
            this.$patch({
                authUser: user,
                isLoggedIn: Boolean(user)
            })
        },
        async createUser(body: any) {
            const res = await useRequest("/users/", {
                method: "POST",
                body: body,
            });

            const userData = res.data?.value;

            if (userData?.user) {
                this.setUser(userData.user);
            }

            return res;
        },
        async login(email: string, password: string, rememberMe?: boolean) {
            const res = await useRequest("/auth/login/", {
                method: "POST",
                body: JSON.stringify({
                    email,
                    password,
                    rememberMe,
                }),
            });

            const userData = res.data?.value as any;

            if (userData?.user) {
                this.setUser(userData.user);
            }

            return res;
        },
        async logout() {
            const csrftoken = useCookie('csrftoken')
            const res = await useRequest('/auth/logout/', {method: 'POST'})
            this.setUser(null)
            csrftoken.value = null
            navigateTo('/')
            return res
        },
        async fetchUser() {
            const fetchUserRequest = useRequest('/users/me/')
            const {data, error, execute} = fetchUserRequest
            await execute()

            if (error.value) {
                this.setUser(null)

                throw new Error(error.value as any)
            }

            if (data?.value as UserT) {
                this.setUser(data.value)
            }

            return {data, error, execute}
        }
    }
});
