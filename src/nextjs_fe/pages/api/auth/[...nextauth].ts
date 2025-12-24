import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    // Mock provider for local development
    CredentialsProvider({
      id: "mock",
      name: "Mock Login",
      credentials: {
        username: { label: "Username", type: "text", placeholder: "mockuser" },
      },
      async authorize(credentials, req) {
        // In dev mode, we allow a mock user
        if (process.env.NODE_ENV === "development" || process.env.NEXT_PUBLIC_ALLOW_MOCK_AUTH === "true") {
           const mockEmail = process.env.MOCK_AUTH_USER || "mock@example.com";
           return {
             id: "mock-123",
             name: "Mock User",
             email: mockEmail,
             image: "/avatars/dazbo.png"
           }
        }
        return null
      }
    })
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      console.log("JWT Callback - Account:", account ? account.provider : "None", "User:", user ? user.name : "None");
      // Persist the OAuth access_token to the token right after signin
      if (account) {
        token.accessToken = account.access_token
        token.idToken = account.id_token
        token.provider = account.provider
      }
      
      // If signing in with the Mock provider (Credentials), generate the expected mock token
      if (user && account && account.provider === 'credentials') {
          // Backend expects format: "mock:id:email:name"
          // We strip 'mock-' prefix from id if present to match backend expectation of integer-like id or just plain id
          const cleanId = user.id.replace('mock-', '');
          token.idToken = `mock:${cleanId}:${user.email}:${user.name}`;
          token.provider = 'mock';
          console.log("Mock token generated:", token.idToken);
      }
      
      return token
    },
    async session({ session, token, user }) {
      console.log("Session Callback - Token ID:", token.idToken ? "exists" : "MISSING");
      // Send properties to the client, like an access_token from a provider.
      session.accessToken = token.accessToken as string
      session.idToken = token.idToken as string
      session.provider = token.provider as string
      if (session.user) {
         session.user.id = token.sub as string
      }
      return session
    }
  },
  secret: process.env.NEXTAUTH_SECRET,
}

export default NextAuth(authOptions)
