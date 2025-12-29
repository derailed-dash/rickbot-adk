# Specification - UI Enhancements: Rick and Morty Aesthetic

## Overview
Enhance the Rickbot-ADK React frontend to more closely align with the "Rick and Morty" visual style. This includes a major theme update focusing on "Portal Green", replacing standard icons with show-themed assets, and adding a signature portal gun animation to the interaction flow.

## Functional Requirements
1.  **Portal Green Theme Update**:
    *   Update the Material UI theme to use neon "Portal Green" (`#39FF14`, `#90E900`) as the primary accent color.
    *   Ensure all primary buttons, highlights, and borders use this green palette.
    *   Maintain a deep black/dark grey background for high contrast.
2.  **"New Chat" Icon Replacement**:
    *   Replace the current `DeleteSweepIcon` (or equivalent) for "New Chat" with a stylized **Plumbus** icon.
3.  **Animated Portal Gun Send Button**:
    *   Replace the standard "Send" button/icon with a **Portal Gun** visual.
    *   **Animation**: On click, trigger a portal opening animation where a swirling green portal appears and the message visualizes as "flying" into the portal.

## Non-Functional Requirements
*   **UI/UX**: Animations must be smooth and not hinder the perceived performance of the application.
*   **Theme Consistency**: The green accents must be legible against the dark background, adhering to accessibility standards (contrast ratios).

## Acceptance Criteria
*   The UI primary accent color is changed from pale blue to neon portal green.
*   The "New Chat" button displays a Plumbus icon.
*   Clicking "Send" triggers a green portal opening animation.
*   The overall aesthetic is consistently "Rick and Morty" themed across the main chat interface.

## Out of Scope
*   Adding new personas or changing agent logic.
*   Modifying the Streamlit frontend.
*   Implementing complex 3D assets (SVG or CSS animations preferred).
