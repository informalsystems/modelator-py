# modelator-py

|⚠️ The tools in this repo are unstable and may be subject to major changes ⚠️|
|-|

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

_**Lightweight utilities to assist model writing and model-based testing activities using the TLA+ ecosystem.**_

## What is this project?

A collection of cli utilities to reduce leg-work when developing TLA+ models, running model checkers, and doing model-based testing. The utilities are also intended to act as building blocks for tool development in the TLA+ ecosystem.

### What can it do right now?

Currently there is a cli implementing utilities:

- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker without side effects (runs in temporary directory and is cleaned up)
- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker programmatically (reads and returns json data)
- [x] ~Run [Apalache](https://github.com/informalsystems/apalache) model checker without side effects (runs in temporary directory and is cleaned up)~ (needs patch)
- [x] ~Run [Apalache](https://github.com/informalsystems/apalache) model checker programmatically (reads and returns json data)~ (needs patch)
- [x] Extract traces from TLC output in [Informal Trace Format](https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format) format (concise and machine readable counterexample representation)

### What will it do in the future?

The model-based testing capabilities developed at Informal are currently in the [modelator](https://github.com/informalsystems/modelator) tool and are being migrated to Python. Please expect more utilities and more tooling soon.

## Running the code in this repository

### Dependencies

- [pyenv](https://github.com/pyenv/pyenv) should be used to manage local Python versions. It can be installed with e.g. `brew install pyenv` (Linux and Windows users should check instructions).
- [Poetry](https://github.com/python-poetry/poetry) is used to manage dependencies and packaging. See the [github](https://github.com/python-poetry/poetry) page for instructions.

### Info

The Python version used is `3.9.9`.

The project has _not_ been published yet so the tools should be run from a development environment (clone the repo, install the dependencies and run the python program directly). It should be easy because we are using [Poetry](https://github.com/python-poetry/poetry).

### New workstation setup for developers, TLDR

1. Install `pyenv`
2. Install `poetry`
3. Clone this repo
4. `cd <repo>`
5. `pyenv install 3.9.9`
6. `poetry env use python`
7. `poetry shell`
8. `poetry install`
9. `code .` to open a VSCode instance with a Python 3.9.9 interpreter (assuming VSCode)

### Commands for devs

With Poetry installed run `poetry install`. Then

- Run the cli program: `poetry run cli <args>` (entrypoint is `modelator/cli:cli`)
- Tests: `poetry run pytest` or use your code editor. VSCode has built in support.
- Tests with coverage: `poetry run pytest --cov=modelator tests/`
- Tests with logging output to terminal: `poetry run pytest --log-cli-level=debug`
- Specific test: `poetry run pytest tests/<dir>/<filename>.py -k 'test_<suffix>'`
- Specific test and display stdout: `poetry run pytest tests/<dir>/<filename>.py -s -k 'test_<suffix>'`
- Run the pre-commit hooks: `pre-commit run --all-files`
- Run linter manually: `flake8 .`
- Run formatter manually: `black .`
- Run static type checker: `mypy .`
- Sort imports `isort .`

### Commands for users

Please see [usage](./usage.md).

### Tips for VSCode users

VSCode has solid support for Python development using Poetry. If VSCode does not pick up on Poetry then try navigating to this directory and executing

```
poetry shell;
code .;
```

Ensure that the bottom left of your VSCode window shows that you are using the correct Python environment.

The branch [vscode-configuration-template](https://github.com/informalsystems/mbt-python/tree/vscode-configuration-template) contains a .vscode directory which can be used as a starting point for configuring your dev environment.

### Troubleshooting

This project has been setup following the guidelines at [this](https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/) blog post. The page contains useful context for troubleshooting.

If having difficulties installing poetry using `curl -sSL https://install.python-poetry.org | python3 -` on MacOS then try adding `eval "$(pyenv init --path)";` to your .bashrc or .zshrc file (given that pyenv is installed).

## Contributing

Coming soon!

## License

Copyright © 2021 Informal Systems Inc. and modelator authors.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use the files in this repository except in compliance with the License. You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
