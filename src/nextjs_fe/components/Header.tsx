import React from 'react';
import { 
    Box, 
    Typography, 
    Avatar, 
    IconButton, 
    Badge, 
    FormControl, 
    InputLabel, 
    Select, 
    MenuItem 
} from '@mui/material';
import AuthButton from './AuthButton';
import { Personality } from '../types/chat';

interface HeaderProps {
    personalities: Personality[];
    selectedPersonality: Personality;
    onPersonalityChange: (p: Personality) => void;
    onClearChat: () => void;
}

export default function Header({ 
    personalities, 
    selectedPersonality, 
    onPersonalityChange, 
    onClearChat 
}: HeaderProps) {
    return (
        <Box 
            component="header"
            sx={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr 1fr', 
                alignItems: 'center', 
                mb: 2,
                gap: 2
            }}
        >
            {/* Column 1: Logo (Left) */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                <Typography 
                    variant="h4" 
                    color="primary" 
                    sx={{ 
                        textShadow: '0 0 10px rgba(57, 255, 20, 0.5)', 
                        fontWeight: 'bold' 
                    }}
                >
                    Rickbot
                </Typography>
            </Box>

            {/* Column 2: Auth (Center) */}
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <AuthButton />
            </Box>

            {/* Column 3: Actions (Right) */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 1 }}>
                <Typography 
                    variant="caption" 
                    color="primary" 
                    sx={{ 
                        fontWeight: 'bold', 
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                        mr: -0.5
                    }}
                >
                    New chat
                </Typography>
                <IconButton color="secondary" onClick={onClearChat} title="Start New Chat">
                    <Badge badgeContent="+" color="primary" overlap="circular" anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
                        <Box 
                            component="img" 
                            src="/meeseeks.webp" 
                            sx={{ width: 40, height: 40 }} 
                            data-testid="meeseeks-box-icon"
                        />
                    </Badge>
                </IconButton>
                <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel 
                        id="personality-select-label" 
                        sx={{ 
                            color: 'secondary.main',
                            '&.Mui-focused': { color: 'secondary.main' }
                        }}
                    >
                        Personality
                    </InputLabel>
                    <Select
                        labelId="personality-select-label"
                        value={selectedPersonality.name}
                        label="Personality"
                        onChange={(e) => {
                            const newP = personalities.find(p => p.name === e.target.value);
                            if (newP) onPersonalityChange(newP);
                        }}
                        sx={{ 
                            color: 'secondary.main',
                            fontWeight: 'bold',
                            '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 64, 255, 0.5)' },
                            '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#FF40FF' },
                            '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#FF40FF' },
                            '.MuiSvgIcon-root': { color: '#FF40FF' }
                        }}
                    >
                        {personalities.map((p) => (
                            <MenuItem key={p.name} value={p.name}>
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Avatar src={p.avatar} sx={{ width: 24, height: 24, mr: 1 }} />
                                    {p.name}
                                </Box>
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Box>
        </Box>
    );
}