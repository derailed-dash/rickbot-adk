import React from 'react';
import { SvgIcon, SvgIconProps } from '@mui/material';

/**
 * PortalGunIcon - A stylized SVG icon of Rick's Portal Gun.
 * Used for the "Send" action.
 */
export default function PortalGunIcon(props: SvgIconProps) {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24" data-testid="portal-gun-icon">
        {/* Handle - Light Grey */}
        <path d="M7 18v3a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-3" fill="#cfd8dc" stroke="#90a4ae" strokeWidth="0.5" />
        
        {/* Main Body - Blue Grey */}
        <path d="M4 13h14v5H4z" fill="#90a4ae" stroke="#546e7a" strokeWidth="0.5" />
        
        {/* Top Bulb Tube - White/Lightest Grey */}
        <path d="M8 13V7a3 3 0 0 1 3-3h2a3 3 0 0 1 3 3v6" fill="#eceff1" stroke="#b0bec5" strokeWidth="0.5" />
        
        {/* The Green Emitter Core */}
        <circle cx="12" cy="8" r="2.5" fill="#39FF14" stroke="#2dbd11" strokeWidth="0.5" />
        
        {/* Detail: Screen/Dial on top */}
        <rect x="10" y="13" width="4" height="2" fill="#37474f" />
        <rect x="11" y="13.5" width="2" height="1" fill="#39FF14" opacity="0.8" />
    </SvgIcon>
  );
}
