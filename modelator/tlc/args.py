from recordclass import recordclass

# mypy: ignore-errors
# flake8: noqa

tlc_args_fields = (
    "aril",
    "checkpoint",
    "cleanup",
    "config",
    "cont",
    "coverage",
    "deadlock",
    "debug",
    "depth",
    "dfid",
    "difftrace",
    "dump",
    "fp",
    "fpbits",
    "fpmem",
    "generate_spec_te",
    "gzip",
    "h",
    "max_set_size",
    "metadir",
    "nowarning",
    "recover",
    "seed",
    "simulate",
    "terse",
    "tool",
    "userfile",
    "view",
    "workers",
    "file",
)

TlcArgs = recordclass(
    "TlcArgs", tlc_args_fields, defaults=(None,) * len(tlc_args_fields)
)
