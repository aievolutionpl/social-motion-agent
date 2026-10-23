# Optional OpenScreen recorder

Full upstream source and skills are pinned in tools/repos/openscreen. Run scripts/bootstrap_library.py to restore them.
The native application itself must be installed from [official releases](https://github.com/getopenscreen/openscreen/releases). Set OPENSCREEN_EXECUTABLE to your installation. No account, personal recording, browser profile or system installer is bundled.

Run python -S scripts/openscreen.py --help for adapter commands.
Read workflows/SCREEN_TUTORIALS.md and .agents/skills/screen-tutorials/SKILL.md before recording.
Unit tests check bounded window selection, error handling and output protection. They do not certify live microphone, camera or desktop capture on your computer.
