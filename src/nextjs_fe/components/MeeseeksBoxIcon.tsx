import React from 'react';
import { SvgIcon, SvgIconProps } from '@mui/material';

/**
 * MeeseeksBoxIcon - A stylized SVG icon of a Mr. Meeseeks Box.
 * Used for the "New Chat" action.
 */
export default function MeeseeksBoxIcon(props: SvgIconProps) {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24" data-testid="meeseeks-box-icon">
        {/* Top Button Base - Darker Grey */}
        <path d="M7 8V6a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2" fill="#546e7a" stroke="none" />
        
        {/* The Big Button - Red */}
        <circle cx="12" cy="5" r="2.5" fill="#e53935" stroke="#b71c1c" strokeWidth="0.5" />
        
        {/* Box Body - Meeseeks Blue */}
        <rect x="4" y="8" width="16" height="13" rx="1" ry="1" fill="#42a5f5" stroke="#1e88e5" strokeWidth="1.5" />
        
        {/* Front Face Highlight/Detail */}
        <rect x="6" y="10" width="12" height="9" rx="0.5" fill="#64b5f6" stroke="none" />
        
        {/* Button Highlight */}
        <ellipse cx="11.5" cy="4" rx="1" ry="0.5" fill="rgba(255,255,255,0.4)" />
    </SvgIcon>
  );
}
