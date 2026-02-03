import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import GitHubProvider from "next-auth/providers/github"
import CredentialsProvider from "next-auth/providers/credentials"

const providers: any[] = [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    }),
];

// Conditionally add Mock Provider
if (process.env.NODE_ENV === "development" || process.env.NEXT_PUBLIC_ALLOW_MOCK_AUTH === "true") {
  providers.push(
    CredentialsProvider({
      id: "mock",
      name: "Mock Login",
      credentials: {
        username: { label: "Username", type: "text", placeholder: "mockuser" },
      },
      async authorize(credentials, req) {
           const mockEmail = process.env.MOCK_AUTH_USER || "mock@example.com";
           return {
             id: "mock-123",
             name: "Mock User",
             email: mockEmail,
             image: "/avatars/dazbo.png"
           }
      }
    })
  )
}

export const authOptions: NextAuthOptions = {
  providers,
  callbacks: {
    async jwt({ token, account, user }) {
      // Persist the OAuth access_token to the token right after signin
      if (account) {
        token.accessToken = account.access_token
        token.idToken = account.id_token
        token.provider = account.provider
        
        // Handle Mock Provider specifically when account is present
        if (account.provider === 'mock' && user) {
             const cleanId = user.id.replace('mock-', '');
             token.idToken = `mock:${cleanId}:${user.email}:${user.name}`;
             token.provider = 'mock';
        }
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
