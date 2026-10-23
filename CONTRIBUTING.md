# Contributing

Open an issue describing the production problem and expected behavior. Keep changes small and provider-neutral.
Use Python 3.11+, Node 22+ and FFmpeg. Install Node dependencies with npm ci.
Run `python -S -B -m unittest discover -s tests -v`, `python -S scripts/smoke_test.py`, and `python -S scripts/release_check.py`.
For render changes also run `python -S studio.py demo --render` and inspect the result.
Do not contribute client footage, voices, credentials or generated production folders.
Use synthetic fixtures. Document actual checks and limitations in pull requests.
