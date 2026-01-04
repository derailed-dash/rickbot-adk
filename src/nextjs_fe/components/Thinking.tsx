import React from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import PsychologyIcon from '@mui/icons-material/Psychology';
import StorageIcon from '@mui/icons-material/Storage';
import MoveToInboxIcon from '@mui/icons-material/MoveToInbox';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

interface ThinkingProps {
  action: string | null;
  activeTool: { name: string; status: 'running' | 'completed' } | null;
}

const toolMap: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  'google_search': {
    label: 'Google Search',
    icon: <SearchIcon fontSize="small" />,
    color: '#4285F4',
  },
  'SearchAgent': {
    label: 'Search Agent',
    icon: <SearchIcon fontSize="small" />,
    color: '#4285F4',
  },
  'file_search': {
    label: 'File Search',
    icon: <StorageIcon fontSize="small" />,
    color: '#FBBC05',
  },
  'transfer_to_agent': {
    label: 'Agent Transfer',
    icon: <MoveToInboxIcon fontSize="small" />,
    color: '#34A853',
  },
};

const Thinking: React.FC<ThinkingProps> = ({ action, activeTool }) => {
  if (!action && !activeTool) return null;

  const toolInfo = activeTool ? toolMap[activeTool.name] : null;
  const displayName = toolInfo ? toolInfo.label : (activeTool?.name || action || 'Thinking...');
  const icon = toolInfo ? toolInfo.icon : <PsychologyIcon fontSize="small" />;
  const color = toolInfo ? toolInfo.color : 'secondary.main';

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, my: 0.5 }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: color,
        animation: activeTool?.status === 'running' ? 'pulse 1.5s infinite ease-in-out' : 'none',
        '@keyframes pulse': {
          '0%': { opacity: 0.6, transform: 'scale(0.95)' },
          '50%': { opacity: 1, transform: 'scale(1.05)' },
          '100%': { opacity: 0.6, transform: 'scale(0.95)' },
        }
      }}>
        {icon}
      </Box>
      <Typography 
        variant="caption" 
        sx={{ 
          fontStyle: 'italic', 
          color: 'text.secondary',
          fontWeight: 'medium',
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}
      >
        {displayName}
        {activeTool?.status === 'running' && '...'}
        {activeTool?.status === 'completed' && ' (Done)'}
      </Typography>
    </Box>
  );
};

export default Thinking;
