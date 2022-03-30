# modelator-py

|⚠️ The tools in this repo are unstable and may be subject to major changes ⚠️|
|-|

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![PyPi version](https://pypip.in/v/$REPO/badge.png)](https://crate.io/packages/$REPO/)
[![Latest Version](https://pypip.in/version/modelator-py/badge.svg)](https://pypi.python.org/pypi/modelator-py/)
[![Downloads](https://pypip.in/download/modelator-py/badge.svg)](https://pypi.python.org/pypi/modelator-py/)

_**Lightweight utilities to assist model writing and model-based testing activities using the TLA+ ecosystem.**_

## What is this project?

A collection of cli utilities to reduce leg-work when developing TLA+ models, running model checkers, and doing model-based testing. The utilities are also intended to act as building blocks for tool development in the TLA+ ecosystem.

### What can it do right now?

Currently there is a cli implementing utilities:

- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker without side effects (runs in temporary directory and is cleaned up)
- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker programmatically (reads and returns json data)
- [x] Run [Apalache](https://github.com/informalsystems/apalache) model checker without side effects (runs in temporary directory and is cleaned up)
- [x] Run [Apalache](https://github.com/informalsystems/apalache) model checker programmatically (reads and returns json data)
- [x] Extract traces from TLC output in [Informal Trace Format](https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format) format (concise and machine readable counterexample representation)

### What will it do in the future?

The model-based testing capabilities developed at Informal are currently in the [modelator](https://github.com/informalsystems/modelator) tool and are being migrated to a multi language architecture. Please expect more utilities and more tooling soon.

## Usage

Please see [usage](./usage.md).

## Running the code in this repository

Please see [contributing](./CONTRIBUTING.md)

## Contributing

Please see [contributing](./CONTRIBUTING.md)

## License

Copyright © 2021 Informal Systems Inc. and modelator authors.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use the files in this repository except in compliance with the License. You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
