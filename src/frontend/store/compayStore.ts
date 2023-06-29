import {defineStore} from 'pinia';
import {useRequest} from '~/composables/useRequest';

export const useCompanyStore = defineStore('company', {
    persist: true,
    state: () => ({
        company: {},
    }),
    actions: {
        async createCompany(body: any) {
            const res = await useRequest<any>("/api/companies/", {
                method: "POST",
                body,
            });

            // Depending on your API, you may need to adjust this:
            if (res.data?.value) {
                this.company = res.data.value
            }

            return res;
        },

        async getCompany(id: number) {
            const res = await useRequest<any>(`/api/companies/${id}`);

            if (res.data?.value) {
                this.company = res.data.value
            }

            return res;
        },
        async updateCompany(id: number, body: any) {
            const res = await useRequest<any>(`/api/companies/${id}`, {
                method: "PATCH",
                body,
            });

            if (res.data?.value) {
                this.company = res.data.value
            }

            return res;
        },
        async deleteCompany(id: number) {
            const res = await useRequest<any>(`/api/companies/${id}`, {
                method: "DELETE",
            });

            // After deleting a company, you might want to reset the store state:
            if (res.data?.value) {
                this.company = {}
            }

            return res;
        },
    },
});
