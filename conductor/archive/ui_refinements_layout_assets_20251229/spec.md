# Specification - UI Refinements: Enhanced Layout & Assets

## Overview
Refine the Rickbot-ADK React frontend by improving layout consistency, visual prominence of key interaction elements, introducing a richer aesthetic, high contrast, and polished typography.

## Functional Requirements
1.  **Unified Input Row Height**:
    *   Adjust the "Send" button height to exactly match the `TextField` height.
2.  **Increased Icon Prominence**:
    *   Increase the size of the `PortalGunIcon` within the Send button.
3.  **Visual Depth & Theming (Phase 2)**:
    *   **Neon Purple Accents**: Introduce a "Neon Purple" secondary color.
    *   **Space/Galaxy Theme**: Implement a background that evokes a space/galaxy setting.
    *   **Typography Enhancements**: Make text more distinct.
    *   **Avatar Styling**: Remove circular borders.
4.  **High Contrast "Blackout" Styling (Phase 3)**:
    *   **Black Containers**: Replace grey backgrounds with solid black.
    *   **Black Borders**: Use solid black borders.
5.  **Final Polish & Typography (Phase 4)**:
    *   **Brighter Pink**: Brighten the "Neon Purple" to a more vibrant "Hot Pink" or "Neon Pink" (e.g., `#FF00FF` or `#E040FB`).
    *   **Unified Pink Strength**: Ensure "Personality Name" and "User Name" labels match the visual weight and brightness of the "Sign Out" button.
    *   **Dropdown Focus Fix**: Prevent the "Personality" dropdown label/outline from turning green on focus; keep it consistent with the secondary theme (pink/purple).
    *   **Friendly Font**: Switch the main chat text font from `Courier New` (monospace) to a friendlier, more readable sans-serif font like `Roboto`, `Open Sans`, or `Inter`, while keeping headers thematic if desired.

## Acceptance Criteria
*   Send button and input are aligned.
*   Icons are prominent and correct (Portal Gun, Meeseeks).
*   Theme is high-contrast black with galaxy background.
*   Pink accent is vibrant and consistent across all elements.
*   Dropdown focus state does not revert to green.
*   Chat text is legible and friendly.