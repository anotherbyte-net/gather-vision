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

# Windows MINGW64
source .venv/Scripts/activate

# install dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements-dev.txt -r requirements.txt

# check for outdated packages
pip list --outdated
```

Run linters:

```bash
python -X dev black --check .
python -X dev ruff .
```

Run tests:

```bash
python -X dev coverage run -m pytest
```

# Create database
python -X dev src/manage.py migrate
python -X dev src/manage.py createcachetable
python -X dev src/manage.py createsuperuser
```

## Generate docs

Generate the docs using pdoc:

```bash
pdoc --docformat google \
  --edit-url gather_vision=https://github.com/anotherbyte-net/gather-vision/blob/main/src/gather_vision/ \
  --search --show-source \
  --output-directory docs \
  ./src/gather_vision
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

GATHER_VISION_VERSION='0.0.4'
pip install --index-url https://test.pypi.org/simple/ --no-deps gather-vision==$GATHER_VISION_VERSION
# or
pip install dist/gather_vision-$GATHER_VISION_VERSION-py3-none-any.whl
```

Test the installed package.

```bash
gather-vision --version
gather-vision --help
gather-vision list
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
