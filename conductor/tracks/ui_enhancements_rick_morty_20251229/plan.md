# Implementation Plan - UI Enhancements: Rick and Morty Aesthetic

## Phase 1: Theme & Portal Green Styling
- [x] Task: Update the Material UI theme definition in `src/nextjs_fe/pages/_app.tsx` (or where theme is defined) to use the new Portal Green palette. ff8a4f4
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to ensure component-level overrides (like the Persona Profile border) use the new theme colors.
- [x] Task: Write Tests: Add a snapshot or style-based test in `src/nextjs_fe/__tests__/Chat.test.tsx` to verify the primary color application. dbebd9d
- [ ] Task: Conductor - User Manual Verification 'Theme & Portal Green Styling' (Protocol in workflow.md)

## Phase 2: Plumbus "New Chat" Icon
- [ ] Task: Source or create a stylized Plumbus SVG/Icon component.
- [ ] Task: Replace `DeleteSweepIcon` in `src/nextjs_fe/components/Chat.tsx` with the new Plumbus icon.
- [ ] Task: Write Tests: Update `Chat.test.tsx` to verify the presence of the Plumbus icon (via aria-label or test-id).
- [ ] Task: Conductor - User Manual Verification 'Plumbus "New Chat" Icon' (Protocol in workflow.md)

## Phase 3: Animated Portal Gun Send Button
- [ ] Task: Implement the Portal Gun SVG and the CSS/Framer Motion animation for the portal opening effect.
- [ ] Task: Integrate the animation into the `handleSendMessage` flow in `src/nextjs_fe/components/Chat.tsx`.
- [ ] Task: Write Tests: Verify the Send button triggers the expected state/animation classes.
- [ ] Task: Conductor - User Manual Verification 'Animated Portal Gun Send Button' (Protocol in workflow.md)
