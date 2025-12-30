import React, { useState } from 'react';
import { 
    Box, 
    Typography, 
    Avatar, 
    IconButton, 
    Badge, 
    FormControl, 
    InputLabel, 
    Select, 
    MenuItem,
    Drawer,
    List,
    ListItem,
    Divider,
    useMediaQuery,
    useTheme
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
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
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    const toggleDrawer = (open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (
            event.type === 'keydown' &&
            ((event as React.KeyboardEvent).key === 'Tab' ||
                (event as React.KeyboardEvent).key === 'Shift')
        ) {
            return;
        }
        setIsDrawerOpen(open);
    };

    const renderPersonaSelector = () => (
        <FormControl sx={{ minWidth: 120, width: isMobile ? '100%' : 'auto' }}>
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
    );

    return (
        <Box 
            component="header"
            sx={{ 
                display: 'grid', 
                gridTemplateColumns: isMobile ? 'auto 1fr auto' : '1fr 1fr 1fr', 
                alignItems: 'center', 
                mb: 2,
                gap: 2
            }}
        >
            {/* Column 1: Logo (Left) */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'center', gap: 1 }}>
                {isMobile && (
                    <IconButton
                        color="primary"
                        aria-label="menu"
                        onClick={toggleDrawer(true)}
                        edge="start"
                    >
                        <MenuIcon />
                    </IconButton>
                )}
                <Typography 
                    variant="h4" 
                    color="primary" 
                    sx={{ 
                        textShadow: '0 0 10px rgba(57, 255, 20, 0.5)', 
                        fontWeight: 'bold',
                        fontSize: isMobile ? '1.5rem' : '2.125rem'
                    }}
                >
                    Rickbot
                </Typography>
            </Box>

            {/* Column 2: Auth (Center) - Hidden on Mobile */}
            {!isMobile && (
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                    <AuthButton />
                </Box>
            )}

            {/* Column 3: Actions (Right) */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 1 }}>
                {!isMobile && (
                    <Typography 
                        variant="caption" 
                        color="primary" 
                        data-testid="new-chat-label"
                        sx={{ 
                            fontWeight: 'bold', 
                            fontFamily: 'Courier New, monospace',
                            lineHeight: 1.1,
                            textAlign: 'right',
                            mr: -0.5
                        }}
                    >
                        New<br />chat
                    </Typography>
                )}
                <IconButton color="secondary" onClick={onClearChat} title="Start New Chat">
                    <Badge badgeContent="+" color="primary" overlap="circular" anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
                        <Box 
                            component="img" 
                            src="/meeseeks.webp" 
                            sx={{ width: isMobile ? 32 : 40, height: isMobile ? 32 : 40 }} 
                            data-testid="meeseeks-box-icon"
                        />
                    </Badge>
                </IconButton>
                {!isMobile && renderPersonaSelector()}
            </Box>

            {/* Mobile Drawer */}
            <Drawer
                anchor="left"
                open={isDrawerOpen}
                onClose={toggleDrawer(false)}
                PaperProps={{
                    sx: {
                        width: 250,
                        bgcolor: 'rgba(0,0,0,0.95)',
                        borderRight: '1px solid rgba(57, 255, 20, 0.3)',
                        p: 2
                    }
                }}
            >
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 4 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                        <AuthButton />
                    </Box>
                    <Divider sx={{ bgcolor: 'rgba(57, 255, 20, 0.2)' }} />
                    <Box>
                        <Typography variant="overline" color="primary" sx={{ display: 'block', mb: 1 }}>
                            Active Persona
                        </Typography>
                        {renderPersonaSelector()}
                    </Box>
                </Box>
            </Drawer>
        </Box>
    );
}
