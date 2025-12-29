# Implementation Plan - UI Refinements: Enhanced Layout & Assets

## Phase 1: Layout & Icon Refinement
- [x] Task: Adjust the `Button` and `TextField` styling in `src/nextjs_fe/components/Chat.tsx` to ensure matching heights (e.g., using `height: '100%'` or fixed consistent values). b35017a
- [x] Task: Increase the `fontSize` or `sx` dimensions of the `PortalGunIcon` within the Send button. b35017a
- [x] Task: Refine Icon Size: Move icon out of `endIcon` prop or further increase `fontSize` to ensure it's visually larger. 8044430
- [x] Task: Replace Meeseeks Box SVG icon with `meeseeks.webp` image. 2526318
- [x] Task: Replace Portal Gun SVG icon with `portal_gun.png` image. cc49258
- [x] Task: Refine "Send" button padding to fix text alignment. 7b7901d
- [x] Task: Write Tests: Update `src/nextjs_fe/__tests__/Chat.test.tsx` to verify component rendering with updated styles. 7b7901d
- [x] Task: Conductor - User Manual Verification 'Layout & Icon Refinement' (Protocol in workflow.md)

## Phase 2: Visual Depth & Theming
- [x] Task: Update `src/nextjs_fe/styles/theme.ts` to define a `secondary` palette with a Neon Purple color (e.g., #b026ff). 389500a
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to remove the border from `Avatar` components. 726b897
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` (and `AuthButton.tsx` if needed) to style "Sign Out", "Personality Name", and "User Name" using the new secondary color and enhanced typography (bold, shadow/glow). 726b897
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to implement a space/galaxy background image or gradient overlay. 726b897
- [x] Task: Write Tests: Verify theme application and component presence with new styles. 726b897

## Phase 3: High Contrast "Blackout" Styling
- [x] Task: Update `src/nextjs_fe/styles/theme.ts` to set default and paper background colors to solid black. ff36ec8
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to replace `rgba(30,30,30,...)` with black (`rgba(0,0,0,...)` or `#000000`). ff36ec8
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` and `AuthButton.tsx` to replace dark grey borders with black. ff36ec8
- [x] Task: Manual Verification: Ensure purple/green text legibility. ff36ec8

## Phase 4: Final Polish & Typography
- [x] Task: Update `src/nextjs_fe/styles/theme.ts` to change `secondary` color to a brighter Neon Pink (e.g., `#E040FB` or `#FF40FF`) and switch default font to `Roboto` or `Inter`. 4945892
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to override `Mui-focused` color for the Personality dropdown to match `secondary.main` instead of `primary.main`. 4945892
- [x] Task: Update `src/nextjs_fe/components/Chat.tsx` to ensure Personality/User labels use `fontWeight: 'bold'` and the correct `textShadow` to match the "Sign Out" button's intensity. 4945892
- [x] Task: Manual Verification: Check font readability, pink vibrancy, and dropdown focus state. 4945892
