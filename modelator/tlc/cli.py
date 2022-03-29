import json as stdjson

from .pure import tlc_pure
from .raw import RawCmd, TlcArgs, tlc_raw


class Tlc:
    def __init__(self, stdin, stdout):
        self._stdin = stdin
        self._stdout = stdout

    def pure(self):
        assert (
            self._stdin is not None
        ), "The pure interface requires json input in stdin"
        json_dict = stdjson.loads(self._stdin.read())

        result = tlc_pure(json=json_dict)
        to_print = stdjson.dumps(result, indent=4, sort_keys=True)
        print(to_print, file=self._stdout)

    def raw(
        self,
        *,
        # Meta args
        json=False,  # Read parameters from Json?
        cwd=None,  # Current working directory to execute TLC
        jar=None,  # Path to tla2tools.jar
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
            json_dict = stdjson.loads(self._stdin.read())
            result = tlc_raw(json=json_dict)
        else:
            """Read instructions from cli flags and arguments"""
            cmd = RawCmd()
            cmd.cwd = cwd
            cmd.jar = jar
            cmd.args = TlcArgs(
                aril,
                checkpoint,
                cleanup,
                config,
                cont,
                coverage,
                deadlock,
                debug,
                depth,
                dfid,
                difftrace,
                dump,
                fp,
                fpbits,
                fpmem,
                generate_spec_te,
                gzip,
                h,
                max_set_size,
                metadir,
                nowarning,
                recover,
                seed,
                simulate,
                terse,
                tool,
                userfile,
                view,
                workers,
                file,
            )
            result = tlc_raw(cmd=cmd)

        stdout_pretty = result.stdout.decode("unicode_escape")
        stderr_pretty = result.stderr.decode("unicode_escape")

        obj_to_print = {}
        obj_to_print["shell_cmd"] = result.args
        obj_to_print["return_code"] = result.returncode
        obj_to_print["stdout"] = stdout_pretty
        obj_to_print["stderr"] = stderr_pretty

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print, file=self._stdout)
