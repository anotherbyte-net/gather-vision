# Gather vision contributing guide

## Development

Create a virtual environment:

```bash
python -m venv .venv
```

Install runtime dependencies and development dependencies:

```bash
# Windows
.venv\Scripts\activate.ps1

# Linux
source .venv/bin/activate

# install dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements-dev.txt -r requirements.txt

# check for outdated packages
pip list --outdated
```

## Run tests and linters

```bash
# Tests - multiple python versions using tox
# (it might be necessary to (un)comment `recreate = true` in pyproject.toml)
python -X dev -m tox

# Tests - Run tests with coverage
python -X dev -m coverage run -m pytest --tb=line --doctest-modules
(
  set -o pipefail
  python -X dev -m pytest --doctest-modules --junitxml=pytest.xml \
    --cov-report=term-missing:skip-covered --cov=src/ tests/ | tee pytest-coverage.txt
)

# Tests - Coverage report
python -X dev -m coverage report

# Linter - flake8
python -X dev -m flake8 src --count --show-source --statistics

# Linter - mypy
python -X dev -m mypy src

# Linter - black
python -X dev -m black --check src

# Linter - pylint
python -X dev -m pylint src

# Linter - pydocstyle
python -X dev -m pydocstyle src

# Linter - pyright
python -X dev -m pyright src

# Linter - pytype
python -X dev -m pytype -j auto
```

## Generate docs

Generate the docs using pdoc3:

```bash
pdoc --html --output-dir docs src/gather_vision --force \
  --config "lunr_search={'fuzziness': 1, 'index_docstrings': True}" \
  --config "git_link_template='https://github.com/anotherbyte-net/gather-vision/blob/{commit}/{path}#L{start_line}-L{end_line}'"
```

## Create and upload release

Generate the distribution package archives.

```bash
python -X dev -m build
```

Upload archives to Test PyPI first.

```bash
python -X dev -m twine upload --repository testpypi dist/*
```

When uploading:

- for username, use `__token__`
- for password, create a token at https://test.pypi.org/manage/account/#api-tokens

Go to the [test project page](https://test.pypi.org/project/gather-vision) and check that it looks ok.

Then create a new virtual environment, install the dependencies, and install from Test PyPI.

```bash
python -m venv .venv-test
source .venv-test/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements.txt

GATHER_VISION_VERSION='0.0.1'
pip install --index-url https://test.pypi.org/simple/ --no-deps gather-vision==$GATHER_VISION_VERSION
# or
pip install dist/gather_vision-$GATHER_VISION_VERSION-py3-none-any.whl
```

Test the installed package.

```bash
gather-vision --version
gather-vision --help
gather-vision list
gather-vision show name
gather-vision update name
```

If the package seems to work as expected, upload it to the live PyPI.

```bash
python -X dev -m twine upload dist/*
```

When uploading:

- for username, use `__token__`
- for password, create a token at https://pypi.org/manage/account/#api-tokens

Go to the [live project page](https://pypi.org/project/gather-vision) and check that it looks ok.

Done!
