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
           return {
             id: "mock-123",
             name: "Mock User",
             email: "mock@example.com",
             image: "/avatars/dazbo.png"
           }
        }
        return null
      }
    })
  ],
  callbacks: {
    async jwt({ token, account }) {
      // Persist the OAuth access_token to the token right after signin
      if (account) {
        token.accessToken = account.access_token
        token.idToken = account.id_token
        token.provider = account.provider
      }
      return token
    },
    async session({ session, token, user }) {
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
