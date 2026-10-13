# Phase 2 — Actual Mac Screenshot Review

Evidence: GitHub Actions run 38354230153, artifact "ACE Adventures 3 Actual Mac Screenshots". The PNG images are screen captures of the real Tk application running on macOS, not mockups.

## Captured screens
1. Exploration — screenshot reviewed; game fits the Mac display, scene and free-text input are visible.
2. Inventory — selected inventory panel now visible, with equipped-item controls.
3. Shop — merchant inventory visible with Buy buttons and the scrollable sidebar.
4. Battle — guardian is visually distinct and ability actions appear, but detailed sprite and VFX quality are not at the reference standard.
5. Story Tree — story nodes are legible in the right column.
6. Map — parchment atlas and place nodes visible, though small at minimum window size.

## Corrected from the first actual screenshot review
- Earlier capture tried to show a 1300x880 window on a 1024x768 Mac screen, cropping off large parts of the actual UI. Capture now fits the game window to the display and validates the bounds.
- Action composer was pushed below the visible edge by tall scene/story elements. It is now fixed to the bottom of the gameplay card, with an explicit native Tk visibility test.
- Full-height character portraits and resource bars obscured all non-character-sheet tabs. Non-record tabs now use a small persistent character summary; Character Sheet retains the full approved-artwork portrait.
- Navigation tabs and map panel compacted to expose the selected content. A real Tk test checks the on-screen position of Shop, Pack, Town, Story Tree and Map content.
- Full Mac build and screenshot checks are passing as of run 38354230153.

## Visual criteria still NOT satisfied
- **Character sprites and portraits:** the screenshots show simplified native block figures because the approved path-specific art pack is not installed in the build. These do not yet match the target of detailed pixel-art fantasy characters.
- **Exploration backgrounds:** native procedural village, market and forest illustrations are much simpler than the weathered, detailed pixel-art fantasy concept environment.
- **Combat character presentation:** monsters and heroes are distinguishable but require cohesive professionally illustrated sprite frames, scale and perspective.
- **Materials and ornamentation:** parchment, wood and brass palettes are consistent but still lack the detailed textures, carved borders and manuscript finishing of the concept references.
- **Animations:** geometric spell effects have distinct school palettes, but full sprite-based animation coverage has not been visually approved.
- **Native UI quality:** desktop screenshots include normal macOS chrome and dock; further scene scale/typography/spacing refinement is appropriate for production.

## Phase 2 acceptance conclusion
Functional interface integration and capture pipeline are complete and regression tested, but aesthetic approval and asset replacement are NOT complete. The build remains a development preview. Do not label Phase 2 as finished, do not ship it as the final concept-matched release, and do not substitute generated concept images for these real screenshots.

## Next correction gate
Use the original concept references and the actual captured PNGs side by side; install verified licensed and explicitly approved class/path character sprites plus environment scenes and full-frame combat art; rerun the macOS workflow and inspect captures again. No visual-perfect signoff is possible without actual approved art and that comparison.
