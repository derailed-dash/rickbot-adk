import { useSession, signIn, signOut } from "next-auth/react"
import { Button, Avatar, Box, Typography } from "@mui/material"

export default function AuthButton() {
  const { data: session } = useSession()

  if (session) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="body1" sx={{ color: 'secondary.main', fontWeight: 'bold', textShadow: '0 0 5px rgba(176, 38, 255, 0.5)' }}>
          {session.user?.name}
        </Typography>
        <Avatar 
          src={session.user?.image || ""} 
          alt={session.user?.name || ""}
          sx={{ width: 32, height: 32 }}
        />
        <Button 
          variant="outlined" 
          color="secondary" 
          size="small"
          onClick={() => signOut()}
          sx={{ 
            fontWeight: 'bold',
            borderWidth: 2,
            '&:hover': {
              borderWidth: 2,
              boxShadow: '0 0 8px rgba(176, 38, 255, 0.6)'
            }
          }}
        >
          Sign out
        </Button>
      </Box>
    )
  }
  return (
    <Button 
      variant="contained" 
      color="primary" 
      size="small"
      onClick={() => signIn()}
    >
      Sign in
    </Button>
  )
}
