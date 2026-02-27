import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
    baseURL: "https://zaferkaraca.net",
    advanced: {
        crossSubDomainCookies: {
            enabled: true,
            domain: ".zaferkaraca.net",
        },
    },
    fetchOptions: {
        credentials: "include",
    },
});
