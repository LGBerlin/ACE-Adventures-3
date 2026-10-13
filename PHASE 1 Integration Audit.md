# Phase 1 Integration Audit — ACE Adventures 3

This document records what the repository and automated Mac tests actually establish. It does not certify live Ollama behaviour on an end-user Mac or the Phase 2 illustrated UI.

## Preserved baseline features
- Four base classes (Fighter, Rogue, Mage, Vessel), 17 class paths, 14 magic schools.
- Character creation/roulette, party selection, progression to level 100, passive and ability unlocks, per-ability training and evolving display effects.
- Free-text game actions, authoritative dice/roll history, encounter and boss rules, party combat, retreat and persistent combat logs.
- The Hollow Bell storyline, gated maps, NPC interactions, journal, story tree, two active-quest limit and repeatable guild assignments.
- Weapons, armor, trinkets, enchantment wheel, scroll study, trading, enemy drops and rare boss loot.
- Tk tabletop interface: party, character record, inventory, abilities, map, story journal, tree, Town, Shop and Dice Board; AI Connections and update/recovery controls.
- Local Ollama narration adapter, deterministic offline action fallback, authoritative state snapshots, bounded pending narration and mocked AI context tests.
- JSON saves and backup recovery, add-on hash verification, origin/path security, rollback and Mac application-release checking.

## Integration defects corrected during this overhaul
1. Two separate boss-victory paths could advance the main quest after unrelated combat. Unified the direct story, UI and text combat paths and gated completion on the actual Hollow Guardian.
2. Former story-choice actions could bypass the shared dice ledger and result processing. Both interaction styles now use the same combat handler.
3. The new and legacy weapon slots could stack bonuses. Equipping either kind displaces the other; selling the last owned copy removes active effects.
4. Generic Mage casting and unauthorized invented spells were conflated. Generic casting chooses an actually learned spell; explicit unlearned spells fail before dice or mana expenditure.
5. AI narration lacked modern equipment, world, quest, class and combat context. It now receives those facts as read-only data, and obvious fabricated victory/reward claims fall back to authoritative results.
6. Several UI actions bypassed AI narration. Story, map, merchant, equipment and inventory controls now pass their verified outcomes to the narrator. Rapid actions retain the latest pending narration.
7. Starter abilities had no higher-rank visual evolution. Ability training now affects damage, defensive strength, displayed ranks and cues without changing saved move identifiers.
8. Save validation covers modern optional fields and rejects symlink redirects while preserving old campaign compatibility.

## Automated evidence
- `run_mac_tests.py` runs test modules in separate processes to avoid Tk lifecycle teardown crashes.
- GitHub Actions on macOS tests quest and combat acceptance, classes/magic catalogs, ability progression, dice/no-dice routes, NPC/guild progression, inventory and enchantments, AI mocked narration, legacy/modern saves, updater security and rollback.
- The workflow builds a native Mac app and runs GUI startup/resource checks. Consult the most recent branch workflow result before treating this pass as green.

## Remaining verification limits / not release-certified
- **Live local AI:** the actual qwen3.5:4b Ollama model, latency, and long-dialogue output on the user's Mac cannot be exercised by mocked CI.
- **Real-device gameplay:** a human needs to complete lengthy sessions with more than one class and a full party; automated flows cannot reveal every usability or balance issue.
- **Native application updates:** the content updater can install and roll back verified data assets; application binary releases are checked for manual installation, not silently self-replaced.
- **Visual assets:** complete parchment-and-wood concept-art fidelity, approved artwork coverage and screenshots are Phase 2, not certified here.
- **Narration accuracy:** the AI cannot change authoritative state, and explicit fabricated rewards are filtered, but natural-language correctness is not mathematically provable.
- **Content depth:** many skills have school/path-specific rules and evolving ranks, but a full unique hand-authored mechanic for every individual named spell remains design work beyond this playable baseline.

## Gate to Phase 2
1. Obtain a green Mac workflow on the final audit commit.
2. Run a local Ollama connection and free-text campaign test on the intended Mac.
3. Manually verify a content update and rollback with a real saved campaign.
4. Capture the unpolished UI state; then begin Phase 2 visual redesign and screenshot iteration.

Do not merge this working branch to main or represent the app as a final release before the remaining gate checks.
