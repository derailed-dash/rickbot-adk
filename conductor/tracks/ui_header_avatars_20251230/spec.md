# Specification: UI Enhancements - Header Layout & User Avatars

## Overview
This track focuses on refining the Rickbot Next.js frontend layout to improve navigation, thematic consistency, and personal identity. We will reorganize the header elements for better balance and integrate user profile avatars directly into the conversation flow.

## Functional Requirements

### 1. Header Reorganization
- **Logo/Title:** "Rickbot" remains on the left side of the header.
- **User Identity (Middle):** The logged-in user's name, avatar, and "Sign out" button (currently encapsulated in `AuthButton`) will be moved to the horizontal center of the header.
- **Action Group (Right):** The "New conversation" (Meeseeks icon) and the "Persona Selector" dropdown will be grouped together on the right side of the header.
- **Mobile Responsiveness:** 
    - Implement a "Hamburger" menu for mobile views.
    - The logo and "New conversation" icon should remain visible.
    - User identity and the Persona Selector should be tucked into the drawer/menu.

### 2. User Avatar in Chat
- **Message Avatars:** In the chat message list, messages sent by the user will now display their actual account avatar if available (retrieved from the `session`).
- **Fallback:** If the user does not have an image associated with their account, or if they are not signed in (though signing in is currently required for chat), the system will fall back to the existing `morty.png` avatar.

## Non-Functional Requirements
- **Theme Consistency:** All new UI elements (like the Hamburger menu) must adhere to the "Portal Green" and "Council of Ricks" neon aesthetic (using existing MUI theme colors).
- **Smooth Transitions:** Use Framer Motion or MUI transitions for the mobile menu opening/closing.

## Acceptance Criteria
- [ ] Header items are correctly positioned on desktop: Logo (Left), User/Auth (Center), New Chat/Persona (Right).
- [ ] User's real avatar appears next to their messages in the chat history.
- [ ] User's messages fall back to Morty avatar if no account image exists.
- [ ] On mobile screens, a Hamburger menu appears.
- [ ] Clicking the Hamburger menu reveals the User/Auth info and Persona Selector.
- [ ] The "New conversation" icon remains easily accessible on mobile.

## Out of Scope
- Backend changes to user profiles.
- Changes to the Streamlit internal UI.
