# mbt-python

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Framework and tools for model-based testing (Python code only. Rust code can be found at [modelator](https://github.com/informalsystems/modelator))

## Running the code in this repository

### Dependencies

- [pyenv](https://github.com/pyenv/pyenv) should be used to manage local Python versions. It can be installed with e.g. `brew install pyenv` (Linux and Windows users should check instructions).
- [Poetry](https://github.com/python-poetry/poetry) is used to manage dependencies and packaging. See the [github](https://github.com/python-poetry/poetry) page for instructions.

### Info

The Python version used is `3.10.0`.

### Running

With Poetry installed `poetry install`.

- Run: `poetry run python <.py file>`.
- Tests: `poetry run pytest` or use your code editor. VSCode has built in support.
- Tests with coverage: `poetry run pytest --cov=modelator tests/`
- Tests with logging output to terminal: `poetry run pytest --log-cli-level=debug`
- Preview the pre-commit hooks: `pre-commit run --all-files`
- Run linter manually: `flake8 .`
- Run formatter manually: `black .`
- Run static type checker: `mypy .`
- Sort imports `isort .`

### Tips for VSCode users

VSCode has solid support for Python development using Poetry. If VSCode does not pick up on Poetry then try navigating to this directory and executing

```
poetry shell
code .
```

Ensure that the bottom left of your VSCode window shows that you are using the correct Python environment (see contents of pyproject.toml for the correct Python version).

### TLDR;

In short, setting up the repo on a new workstation might look like

1. Install pyenv
2. Install poetry
3. Clone repo
4. `cd` repo
5. `pyenv install x.x.x`
6. `poetry env use python`
7. `poetry shell`
8. `poetry install`
9. `code .` (for VSCode)

### Troubleshooting

This project has been setup following the guidelines at [this](https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/) blog post. The page contains useful context for troubleshooting.

If having difficulties with `poetry install` on linux due to a missing `_ctypes` module then consider the advice on [this](https://stackoverflow.com/a/41310760) stack overflow page, and on [this](https://github.com/pyenv/pyenv/issues/2137) issue.

## Contributing

Coming soon!

## License

Copyright © 2021 Informal Systems Inc. and modelator authors.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use the files in this repository except in compliance with the License. You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
