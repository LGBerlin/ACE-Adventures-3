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


## Current native build status (October 2026)
A self-contained **experimental** Mac launch baseline is in `app.py`. It supports campaigns, permanent rolled characters, a short quest, D20 combat, saves, local Ollama narration, and service diagnostics for Ollama/ComfyUI. It does **not** yet contain the illustrated prototype's complete visual and gameplay systems, ComfyUI image-generation workflow, full add-on updater, or the full acceptance-test suite. A successful packaging job does not mean that this is the final game.


## Validation candidate
The illustrated gameplay source and 37 automated regressions are present; GitHub must verify the packaged native application before any release is described as ready.
