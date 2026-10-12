# ACE Adventures 3

Standalone fantasy RPG project for Apple Silicon macOS. **Development status: no verified Mac release yet.**

The goal is a story-driven D20 adventure with campaigns, permanent character creation, persistent towns and NPCs, inventory, visual encounters, and local Ollama Dungeon Master support. ComfyUI is an optional external art service.

## Release requirements
1. Migrate and test the complete application source.
2. Build an actual `.app` on a macOS Apple Silicon runner.
3. Confirm packaged executable architecture and startup.
4. Test save/reopen, campaign progression, external AI failures, and update recovery.
5. Provide a signed/notarized release when possible; until then clearly mark unsigned builds.

**No source-only ZIP is a Mac application.** The build workflow deliberately fails when the full source is missing.


## Phase 1 baseline status (October 2026)

The **Phase 1 functional baseline and repository-wide integration audit** are implemented on development branch `feature/tabletop-ui-shop-20261012`. GitHub Actions on `macos-15` runs the isolated automated test suite, native Apple Silicon app packaging, graphical startup smoke tests, and idle-resource check.

Implemented gameplay includes: four classes, 17 paths, 14 magic schools, character roulette and level-100 progression; free-text D20 actions; quests capped at two active assignments, townsfolk and guild progression; party combat, bosses and loot; weapons/armor/trinkets, enchantments, scrolls, trading; persistent saves and content update/rollback; local Ollama narration with a deterministic state-changing rules engine.

**Phase 1 functionality is not a notarized public release.** Automated tests cannot establish the quality or latency of a real Ollama model over a long session on the player's Mac. The built-in app-release checker requires manual app installation; it cannot update binaries automatically. Final signed/notarized delivery and pixel-perfect concept-art visuals are not covered by the Phase 1 baseline.

See [PHASE 1 Integration Audit.md](PHASE%201%20Integration%20Audit.md) for the actual covered tests and outstanding device-specific acceptance checks. Phase 2 is the planned visual redesign, not yet a completed art pack.
