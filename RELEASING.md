# Releasing `kratix-sdk`

This document captures the steps for cutting a new version of the SDK and publishing it to PyPI.

1. **Prep the repo**
   - Update `pyproject.toml` with the new version under `[tool.poetry]`.
   - Add an entry to `CHANGELOG.md` summarising the release and changes.
   - Commit your work before building artifacts.

2. **Run quality checks**
   ```bash
   make install          # installs dependencies
   make fmt && make lint # optional but recommended
   make test             # run pytest
   ```

3. **Build distributions**
   ```bash
   poetry build
   ls dist/              # verify the wheel and sdist exist
   tar tf dist/kratix-sdk-<version>.tar.gz | head
   ```
   Inspect the contents to ensure only expected files are included.

4. **Publish to TestPyPI (recommended)**
   ```bash
   poetry publish --repository testpypi --build
   python -m venv /tmp/kratix-sdk-test
   source /tmp/kratix-sdk-test/bin/activate
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple kratix-sdk==<version>
   ```
   Run a quick smoke test (`python -c "import kratix_sdk; print(kratix_sdk.__version__)"`) to ensure the build works.

5. **Publish to PyPI**
   ```bash
   poetry publish --build
   git tag v<version>
   git push origin main --tags
   ```
   PyPI credentials/API token must be configured in `~/.pypirc` beforehand.

6. **Communicate the release**
   - Share release notes on the relevant channels.
   - Update downstream sample projects if they pin versions.

