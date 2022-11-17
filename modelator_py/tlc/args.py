from dataclasses import dataclass
from typing import Optional

# mypy: ignore-errors
# flake8: noqa


@dataclass
class TlcArgs:
    aril: Optional[str] = None
    checkpoint: Optional[str] = None
    cleanup: Optional[str] = None
    config: Optional[str] = None
    cont: Optional[str] = None
    coverage: Optional[str] = None
    deadlock: Optional[str] = None
    debug: Optional[str] = None
    depth: Optional[str] = None
    dfid: Optional[str] = None
    difftrace: Optional[str] = None
    dump: Optional[str] = None
    fp: Optional[str] = None
    fpbits: Optional[str] = None
    fpmem: Optional[str] = None
    generate_spec_te: Optional[str] = None
    gzip: Optional[str] = None
    h: Optional[str] = None
    max_set_size: Optional[str] = None
    metadir: Optional[str] = None
    nowarning: Optional[str] = None
    recover: Optional[str] = None
    seed: Optional[str] = None
    simulate: Optional[str] = None
    terse: Optional[str] = None
    tool: Optional[str] = None
    userfile: Optional[str] = None
    view: Optional[str] = None
    workers: Optional[str] = None
    file: Optional[str] = None
