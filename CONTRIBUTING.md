# Contributing

Open an issue describing the production problem and expected behavior. Keep changes small and provider-neutral.
Use Python 3.11+, Node 22+ and FFmpeg. Prepare local Node dependencies with `python -S studio.py setup`.
Run `python -S -B -m unittest discover -s tests -v`, `python -S scripts/smoke_test.py`, and `python -S scripts/release_check.py`.
For render changes also run `python -S studio.py demo --render` and inspect the result.
Do not contribute client footage, voices, credentials or generated production folders.
Use synthetic fixtures. Document actual checks and limitations in pull requests.

## Browser layout tests

The core suite uses `-S` and does not require pip packages. For the browser tests, use a virtual environment and run without `-S` so that Playwright can be imported:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m unittest discover -s tests -p test_polish.py -v
```

On Linux, `python -m playwright install --with-deps chromium` can also install the required browser system libraries. CI has a separate browser job that requires the starter layout tests to run without skips, plus a Windows core/FFmpeg smoke job. Existing Linux jobs retain the full-library checks and actual HyperFrames renders.
