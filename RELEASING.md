# Releasing `kratix-sdk`

This document captures the steps for cutting a new version of the SDK and publishing it to PyPI.

1. **Set up Poetry credentials (one-time per machine)**
   ```bash
   poetry config repositories.testpypi https://test.pypi.org/legacy/
   # Use a TestPyPI API token copied from https://test.pypi.org/manage/account/token/
   poetry config pypi-token.testpypi <TESTPYPI_API_TOKEN>
   # For the main PyPI token (if not already configured)
   poetry config pypi-token.pypi <PYPI_API_TOKEN>
   ```
   Alternatively export `POETRY_HTTP_BASIC_TESTPYPI_USERNAME="__token__"` and `POETRY_HTTP_BASIC_TESTPYPI_PASSWORD="<token>"` before publishing.

2. **Prep the repo**
   - Update `pyproject.toml` with the new version under `[tool.poetry]`.
   - Add an entry to `CHANGELOG.md` summarising the release and changes.
   - Commit your work before building artifacts.

3. **Run quality checks**
   ```bash
   make install          # installs dependencies
   make fmt && make lint # optional but recommended
   make test             # run pytest
   ```

4. **Build distributions**
   ```bash
   poetry build
   ls dist/              # verify the wheel and sdist exist
   tar tf dist/kratix-sdk-<version>.tar.gz | head
   ```
   Inspect the contents to ensure only expected files are included.

5. **Publish to TestPyPI (recommended)**
   ```bash
   poetry publish --repository testpypi --build
   python -m venv /tmp/kratix-sdk-test
   source /tmp/kratix-sdk-test/bin/activate
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple kratix-sdk==<version>
   ```
   Run a quick smoke test (`python -c "import kratix_sdk; print(kratix_sdk.__version__)"`) to ensure the build works.

6. **Publish to PyPI**
   ```bash
   poetry publish --build
   git tag v<version>
   git push origin main --tags
   ```
   PyPI credentials/API token must be configured in `~/.pypirc` beforehand.

7. **Communicate the release**
   - Share release notes on the relevant channels.
   - Update downstream sample projects if they pin versions.
