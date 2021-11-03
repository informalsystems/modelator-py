import logging
import os
from pathlib import Path

from modelator.apalache import Apalache

LOG = logging.getLogger(__name__)


def test_apalache_raw():
    this_file_path = Path(__file__)
    project_dir = this_file_path.parent.parent
    apalache_jar = "apalache-pkg-0.17.0-full.jar"
    apalache_path = os.path.join(project_dir, apalache_jar)
    LOG.debug(apalache_path)
    Apalache(None)
    assert 0
