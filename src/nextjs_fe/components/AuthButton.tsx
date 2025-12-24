import { useSession, signIn, signOut } from "next-auth/react"
import { Button, Avatar, Box, Typography } from "@mui/material"

export default function AuthButton() {
  const { data: session } = useSession()

  if (session) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="body2" sx={{ color: 'white' }}>
          {session.user?.name}
        </Typography>
        <Avatar 
          src={session.user?.image || ""} 
          alt={session.user?.name || ""}
          sx={{ width: 32, height: 32 }}
        />
        <Button 
          variant="outlined" 
          color="inherit" 
          size="small"
          onClick={() => signOut()}
          sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
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
