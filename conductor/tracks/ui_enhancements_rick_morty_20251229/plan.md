# Implementation Plan - UI Enhancements: Rick and Morty Aesthetic

## Phase 1: Theme & Portal Green Styling [checkpoint: 9e36922]
- [x] Task: Update the Material UI theme definition in `src/nextjs_fe/pages/_app.tsx` (or where theme is defined) to use the new Portal Green palette. ff8a4f4
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to ensure component-level overrides (like the Persona Profile border) use the new theme colors.
- [x] Task: Write Tests: Add a snapshot or style-based test in `src/nextjs_fe/__tests__/Chat.test.tsx` to verify the primary color application. dbebd9d
- [x] Task: Conductor - User Manual Verification 'Theme & Portal Green Styling' (Protocol in workflow.md) dbebd9d

## Phase 2: Plumbus / Meeseeks Box "New Chat" Icon [checkpoint: c3b58c6]
- [x] Task: Source or create a stylized Plumbus SVG/Icon component. d303724
- [x] Task: Replace `DeleteSweepIcon` in `src/nextjs_fe/components/Chat.tsx` with the new Plumbus icon. d303724
- [x] Task: Write Tests: Update `Chat.test.tsx` to verify the presence of the Plumbus icon (via aria-label or test-id). d303724
- [x] Task: Refine Plumbus Icon: Increase size and add 'New Chat' visual clue (Badge/+). d303724
- [x] Task: Conductor - User Manual Verification 'Plumbus "New Chat" Icon' (Protocol in workflow.md) d303724
- [x] Task: Replace Plumbus icon with Mr. Meeseeks Box SVG icon. 3368c43
- [x] Task: Conductor - User Manual Verification 'Meeseeks Box "New Chat" Icon' (Protocol in workflow.md) 3368c43

## Phase 3: Animated Portal Gun Send Button
- [ ] Task: Implement the Portal Gun SVG and the CSS/Framer Motion animation for the portal opening effect.
- [ ] Task: Integrate the animation into the `handleSendMessage` flow in `src/nextjs_fe/components/Chat.tsx`.
- [ ] Task: Write Tests: Verify the Send button triggers the expected state/animation classes.
- [ ] Task: Conductor - User Manual Verification 'Animated Portal Gun Send Button' (Protocol in workflow.md)
