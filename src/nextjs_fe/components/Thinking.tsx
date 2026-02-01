import React from 'react';
import { Box, Typography } from '@mui/material';
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
  'SearchAgent': {
    label: 'Google Search',
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
  'RagAgent': {
    label: 'RagAgent',
    icon: <PsychologyIcon fontSize="small" />,
    color: '#39FF14', // Match portal green for consistency with the screenshot
  },
  'Responding': {
    label: 'Responding',
    icon: <PsychologyIcon fontSize="small" />,
    color: '#39FF14', // Portal Green
  }
};

const Thinking: React.FC<ThinkingProps> = ({ action, activeTool }) => {
  if (!action && !activeTool) return null;

  const isResponding = action === 'Responding...';
  const toolName = activeTool?.name || (isResponding ? 'Responding' : null);
  const toolInfo = toolName ? toolMap[toolName] : null;
  
  const displayName = toolInfo ? toolInfo.label : (activeTool?.name || action || 'Thinking...');
  const icon = toolInfo ? toolInfo.icon : <PsychologyIcon fontSize="small" />;
  const color = toolInfo ? toolInfo.color : '#39FF14'; // Default to Portal Green

  const isRunning = activeTool?.status === 'running' || action === 'Thinking...' || isResponding;

  return (
    <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', gap: 1, my: 0.5 }}>
      <Box component="span" sx={{ 
        display: 'inline-flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: color,
        filter: `drop-shadow(0 0 2px ${color})`,
        animation: isRunning ? 'pulse 1.5s infinite ease-in-out' : 'none',
        '@keyframes pulse': {
          '0%': { opacity: 0.6, transform: 'scale(0.95)' },
          '50%': { opacity: 1, transform: 'scale(1.1)' },
          '100%': { opacity: 0.6, transform: 'scale(0.95)' },
        }
      }}>
        {icon}
      </Box>
      <Typography 
        variant="caption" 
        sx={{ 
          fontStyle: 'italic', 
          color: color,
          opacity: 0.8,
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          textShadow: `0 0 5px ${color}44`
        }}
      >
        {displayName}
        {activeTool?.status === 'running' && '...'}
        {activeTool?.status === 'completed' && ' (Done)'}
        {(!activeTool && action === 'Thinking...') && '...'}
      </Typography>
    </Box>
  );
};

export default Thinking;
