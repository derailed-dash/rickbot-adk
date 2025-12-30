# Plan: UI Enhancements - Header Layout & User Avatars

This plan follows the Test-Driven Development (TDD) workflow to reorganize the header and integrate user avatars into the chat interface.

## Phase 1: User Avatar Integration [checkpoint: 3c2a360]
- [x] Task: Write unit test in `src/nextjs_fe/__tests__/Chat.test.tsx` to verify user message avatar source (Session image vs Fallback) c124739
- [x] Task: Update `Chat.tsx` to pass the session user image to the message list avatar c124739
- [x] Task: Verify user messages correctly display the logged-in user's avatar or fallback to `morty.png` c124739
- [x] Task: Conductor - User Manual Verification 'User Avatar Integration' (Protocol in workflow.md)

## Phase 2: Desktop Header Reorganization [checkpoint: 2950752]
- [x] Task: Extract header logic from `Chat.tsx` into a new `Header` component for better maintainability 5915d28
- [x] Task: Write unit tests for the `Header` component layout positions (Logo Left, Auth Center, Actions Right) 5915d28
- [x] Task: Implement the 3-column flex layout in the `Header` component 5915d28
- [x] Task: Integrate the new `Header` component back into `Chat.tsx` 5915d28
- [x] Task: Conductor - User Manual Verification 'Desktop Header Reorganization' (Protocol in workflow.md)

## Phase 3: Mobile Responsiveness (Hamburger Menu)
- [x] Task: Write unit tests for `Header` component responsive behavior (Drawer visibility at mobile breakpoints)
- [x] Task: Implement `IconButton` (MenuIcon) and `Drawer` for mobile navigation
- [x] Task: Move `AuthButton` and `Persona Selector` into the `Drawer` for mobile views
- [x] Task: Ensure the "New conversation" (Meeseeks) icon remains visible in the top bar on mobile
- [x] Task: Conductor - User Manual Verification 'Mobile Responsiveness' (Protocol in workflow.md)
