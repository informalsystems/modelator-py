# Contributing

Thank you for your interest in contributing to modelator-py!

This document gives best practices for contributing:

- [Development](#development) - how to develop
- [Architecture](#architecture-summary) - project architecture
- [Proposing Changes](#proposing-changes) - process for agreeing to changes
- [Forking](#forking) - fork the repo to make pull requests
- [Pull Requests](#pull-requests) - what makes a good pull request

## Development

### Dependencies

- [pyenv](https://github.com/pyenv/pyenv) should be used to manage local Python versions. It can be installed with e.g. `brew install pyenv` (Linux and Windows users should check instructions).
- [Poetry](https://github.com/python-poetry/poetry) is used to manage dependencies and packaging. See the [github](https://github.com/python-poetry/poetry) page for instructions.

### Python version

The Python version used is `3.9.9`.

### Packaging

The project has _not_ been published or packaged yet so the tools should be run from a development environment (clone the repo, install the dependencies and run the python program directly). It should be easy because we are using [Poetry](https://github.com/python-poetry/poetry).

### Setting up a workstation

1. Install `pyenv`
2. Install `poetry`
3. Clone this repo
4. `cd <repo>`
5. `pyenv install 3.9.9`
6. `poetry env use python`
7. `poetry shell`
8. `poetry install`
9. `code .` to open a VSCode instance with a Python 3.9.9 interpreter (assuming VSCode)

### Useful commands

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

### VSCode Tips

VSCode has solid support for Python development using Poetry. If VSCode does not pick up on Poetry then try navigating to this directory and executing

```bash
poetry shell;
code .;
```

Ensure that the bottom left of your VSCode window shows that you are using the correct Python environment.

The branch [vscode-configuration-template](https://github.com/informalsystems/mbt-python/tree/vscode-configuration-template) contains a .vscode directory which can be used as a starting point for configuring your dev environment.

### Troubleshooting

This project has been setup following the guidelines at [this](https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/) blog post. The page contains useful context for troubleshooting.

If having difficulties installing poetry using `curl -sSL https://install.python-poetry.org | python3 -` on MacOS then try adding `eval "$(pyenv init --path)";` to your .bashrc or .zshrc file (given that pyenv is installed).

## Architecture summary

The project is setup as both a cli program and a collection of pure functions. The cli is an interface to use the pure functions but the pure functions can also be used directly by including modelator-py as a dependency and importing it into your python program. The launch point of the cli is in `modelator/cli::cli`. This is specified in `pyproject.toml::tool.poetry.scripts`.

The cli uses the [python-fire](https://github.com/google/python-fire) library. Documentation for cli commands is inferred [1](https://github.com/google/python-fire/blob/master/fire/docstrings.py)[2](https://github.com/google/python-fire/issues/237#issuecomment-605653263) from [python docstrings](https://peps.python.org/pep-0257/). [Here's](https://github.com/informalsystems/modelator-py/blob/c87d0985d9b40d2d2980216eadbbf2b3ca2e8998/modelator/cli.py#L15-L26) an example.

The [recordclass](https://pypi.org/project/recordclass/) library is another commonly used library. It provides a simple struct like type that is somewhat missing from the python language.

## Proposing Changes

When contributing to the project, adhering to the following guidelines will
dramatically increase the likelihood of changes being accepted quickly.

### Create/locate an issue

1. A good place to start is to search through the [existing
   issues](https://github.com/informalsystems/modelator-py/issues) for the
   problem you're encountering.
2. If no relevant issues exist, submit one describing the _problem_ you're
   facing, as well as a _definition of done_. A definition of done, which tells
   us how to know when the issue can be closed, helps us to scope the problem
   and give it definite boundaries. Without a definition of done, issues can
   become vague.

## Forking

If you do not have write access to the repository, your contribution should be
made through a fork on GitHub. Fork the repository, contribute to your fork, and
make a pull request back upstream.

When forking, add your fork's URL as a new git remote in your local copy of the
repo. For instance, to create a fork and work on a branch of it:

- Create the fork on GitHub, using the fork button.
- `cd` to the original clone of the repo on your machine
- `git remote rename origin upstream`
- `git remote add origin git@github.com:<location of fork>`

Now `origin` refers to your fork and `upstream` refers to this version.

`git push -u origin master` to update the fork, and make pull requests against
this repo.

To pull in updates from the origin repo, run

- `git fetch upstream`
- `git rebase upstream/master` (or whatever branch you want)

## Pull Requests

PRs should:

- make reference to an issue outlining the context.
- update any relevant documentation and include tests.

Commits should be concise but informative, and moderately clean. Commits will be
squashed into a single commit for the PR with all the commit messages.

### Draft PRs

When the problem as well as proposed solution are well understood, changes
should start with a [draft pull request](https://github.blog/2019-02-14-introducing-draft-pull-requests/)
against master. The draft signals that work is underway. When the work is ready
for feedback, hitting "Ready for Review" will signal to the maintainers to take
a look. Maintainers will not review draft PRs.
