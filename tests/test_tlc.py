import logging

from modelator.tlc.raw import (
    TlcArgs,
    RawCmd,
    exec_tlc_raw_cmd,
    stringify_raw_cmd,
)

from .util import get_resource_dir, get_tlc_path

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.mem = False
    cmd.cleanup = False
    cmd.jar = get_tlc_path()
    cmd.cwd = get_resource_dir()
    args = TlcArgs()
    args.cleanup = True
    args.workers = "'auto'"
    args.config = "2PossibleTracesTlc.cfg"
    args.file = "2PossibleTraces.tla"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


# @pytest.mark.skip(
# reason="The 'tlc raw' command has side effects like dirtying the filesystem"
# )
def test_raw_directly():
    # java -jar tla2tools.jar tlc2.TLC -cleanup -workers 'auto' -config 2PossibleTracesTlc.cfg 2PossibleTraces.tla
    cmd = RawCmd()
    cmd.mem = False
    cmd.cleanup = False
    cmd.jar = get_tlc_path()
    cmd.cwd = get_resource_dir()
    args = TlcArgs()
    args.cleanup = False
    args.workers = "'auto'"
    args.config = "2PossibleTracesTlc.cfg"
    args.file = "2PossibleTraces.tla"
    args.userfile = "dans-userfile.txt"
    cmd.args = args
    LOG.debug(stringify_raw_cmd(cmd))
    result = exec_tlc_raw_cmd(cmd)
    LOG.debug(result.process.stdout.decode("unicode_escape"))
    LOG.debug(result.process.stderr.decode("unicode_escape"))
    # LOG.debug("\n".join(list(result.files.keys())))

    assert 0
