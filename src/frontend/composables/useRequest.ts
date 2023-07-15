import {MaybeRef} from '@vueuse/core';

export const useRequest = <T = any>(url: MaybeRef<string>, opts?: Omit<RequestInit, 'body'> & { body?: any }) => {
    const config = useRuntimeConfig();
    const csrfToken = useCookie('csrftoken');
    const headers = {
        'X-CSRFToken': csrfToken.value || '',
        'Content-Type': 'application/json', // Maybe dont' want this here? TODO
        ...opts?.headers,
    };
    const method = (opts?.method?.toUpperCase() || 'GET') as 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'OPTIONS';

    const body = opts?.body ? JSON.stringify(opts.body) : undefined;

    return useFetch<T>(url, {
        baseURL: `${config.public.server_url}`,
        credentials: 'include',
        headers,
        // @ts-ignore
        method,
        body,
        ...opts,
    });
};
