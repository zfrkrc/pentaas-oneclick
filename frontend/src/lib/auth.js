import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
    baseURL: "https://zaferkaraca.net",
    // Cross subdomain session handler if needed
});
