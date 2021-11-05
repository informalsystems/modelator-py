import json

from .pure import apalache_pure
from .raw import ApalacheArgs, RawCmd, apalache_raw


class Apalache:
    def __init__(self, stdin):
        self.stdin = stdin

    def pure(self):
        assert self.stdin is not None
        data = json.loads(self.stdin.read())
        result = apalache_pure(json_obj=data)
        print(result)

    def raw(
        self,
        *,
        stdin=None,
        mem=False,
        cleanup=False,
        cwd=None,
        jar=None,
        cmd=None,
        file=None,
        debug=None,
        out_dir=None,
        profiling=None,
        smtprof=None,
        write_intermediate=None,
        algo=None,
        cinit=None,
        config=None,
        discard_disabled=None,
        init=None,
        inv=None,
        length=None,
        max_error=None,
        next=None,
        no_deadlock=None,
        nworkers=None,
        smt_encoding=None,
        tuning=None,
        tuning_options=None,
        view=None,
        enable_stats=None,
        output=None,
        before=None,
        action=None,
        assertion=None,
        infer_poly=None,
    ):
        result = None
        if stdin:
            data = json.loads(self.stdin.read())
            result = apalache_raw(json_obj=data)
        else:
            raw_cmd = RawCmd()
            raw_cmd.mem = mem
            raw_cmd.cleanup = cleanup
            raw_cmd.cwd = cwd
            raw_cmd.jar = jar
            raw_cmd.args = ApalacheArgs(
                cmd,
                file,
                debug,
                out_dir,
                profiling,
                smtprof,
                write_intermediate,
                algo,
                cinit,
                config,
                discard_disabled,
                init,
                inv,
                length,
                max_error,
                next,
                no_deadlock,
                nworkers,
                smt_encoding,
                tuning,
                tuning_options,
                view,
                enable_stats,
                output,
                before,
                action,
                assertion,
                infer_poly,
            )

            result = apalache_raw(cmd=raw_cmd)

        stdout_pretty = result.process.stdout.decode("unicode_escape")
        stderr_pretty = result.process.stderr.decode("unicode_escape")

        print(
            f"""Ran 'apalache raw'.
shell cmd used: {result.process.args}
subprocess return code: {result.process.returncode}
apalache output files: {result.files}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )
