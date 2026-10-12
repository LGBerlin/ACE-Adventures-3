"""Refuse production builds that omit the illustrated game engine."""
from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parent
MODULES=('app','game','story','story_tree','dungeon_master','ai','ai_connections','art','update_addons','addon_updates','asset_registry','animation_director','visual_mapping','comfy_art')
TESTS=('test_game.py','test_story_addons.py','test_dungeon_master.py','test_reliability.py','test_updater_security.py','test_combat_regression.py','test_rollback_safety.py','test_asset_registry.py','test_animation_director.py','test_story_tree.py','test_roulette_spec.py','test_mac_gui.py','test_mac_adventure_acceptance.py','test_idle_performance.py','test_visual_mapping.py','test_dm_visual_contract.py')
def verify(root=ROOT):
    root=Path(root)
    missing=[str(root/(m+'.py')) for m in MODULES if not (root/(m+'.py')).is_file()]
    missing += [str(root/f) for f in TESTS if not (root/f).is_file()]
    if missing:
        raise RuntimeError('Cannot build incomplete ACE Adventures 3: '+', '.join(missing))
    for module in MODULES:
        src=root/(module+'.py')
        ast.parse(src.read_text(encoding='utf-8'),filename=str(src))
    if (root/'app.py').stat().st_size < 9000:
        raise RuntimeError('Refusing the small fallback launcher: illustrated app source required')
    app=(root/'app.py').read_text(encoding='utf-8')
    if 'import game,ai,story,art,ai_connections' not in app:
        raise RuntimeError('Packaged app must use the integrated illustrated engine')
    return True
if __name__=='__main__':
    verify()
    print('ACE Adventures 3 illustrated release preflight passed')
