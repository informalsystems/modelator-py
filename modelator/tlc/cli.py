import json

from .pure import tlc_pure
from .raw import RawCmd, TlcArgs, tlc_raw


class Tlc:
    def __init__(self, stdin):
        self.stdin = stdin

    def pure(self):
        assert self.stdin is not None, "The pure interface requires json input in stdin"
        content = self.stdin.read()
        data = json.loads(content)
        result = tlc_pure(json_obj=data)
        print(result)

    def raw(
        self,
        *,
        # Meta args
        json=False,  # Read parameters from Json
        mem=False,  # Read TLC outputs into memory
        clean=False,  # Cleanup all evidence of execution
        cwd=None,  # Current working directory to execute TLC
        jar=None,  # path to tla2tools.jar
        # TLC args
        aril=None,
        checkpoint=None,
        cleanup=None,
        config=None,
        cont=None,
        coverage=None,
        deadlock=None,
        debug=None,
        depth=None,
        dfid=None,
        difftrace=None,
        dump=None,
        fp=None,
        fpbits=None,
        fpmem=None,
        generate_spec_te=None,
        gzip=None,
        h=None,
        max_set_size=None,
        metadir=None,
        nowarning=None,
        recover=None,
        seed=None,
        simulate=None,
        terse=None,
        tool=None,
        userfile=None,
        view=None,
        workers=None,
        file=None,
    ):
        """
        Execute TLC
        """
        result = None
        if json:
            """Read instructions from json"""
            data = json.loads(self.stdin.read())
            result = tlc_raw(json=data)
        else:
            """Read instructions from cli flags and arguments"""
            raw_cmd = RawCmd()
            raw_cmd.cwd = cwd
            raw_cmd.jar = jar
            raw_cmd.args = TlcArgs()
            result = tlc_raw(raw_cmd)

        stdout_pretty = result.stdout.decode("unicode_escape")
        stderr_pretty = result.stderr.decode("unicode_escape")

        print(
            f"""Ran 'tlc raw'.
shell cmd used: {result.args}
subprocess return code: {result.returncode}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )
