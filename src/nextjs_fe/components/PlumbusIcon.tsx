import React from 'react';
import { SvgIcon, SvgIconProps } from '@mui/material';

/**
 * PlumbusIcon - A stylized SVG icon of a Plumbus from Rick and Morty.
 * Used for the "New Chat" action.
 */
export default function PlumbusIcon(props: SvgIconProps) {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24" data-testid="plumbus-icon">
      {/* Simplified Stylized Plumbus SVG Path */}
      <path
        d="M12,2C10.9,2,10,2.9,10,4v2h4V4C14,2.9,13.1,2,12,2z M12,8c-3.31,0-6,2.69-6,6c0,2.21,1.79,4,4,4h4c2.21,0,4-1.79,4-4 C18,10.69,15.31,8,12,8z M12,16c-1.1,0-2-0.9-2-2s0.9-2,2-2s2,0.9,2,2S13.1,16,12,16z M8,14c0-2.21,1.79-4,4-4s4,1.79,4,4s-1.79,4-4,4 S8,16.21,8,14z M10,20c0,1.1,0.9,2,2,2s2-0.9,2-2h-4z"
        fill="currentColor"
      />
    </SvgIcon>
  );
}
