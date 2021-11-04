import json

from .pure import PureCmd, exec_apalache_pure_cmd
from .raw import ApalacheArgs, RawCmd, exec_apalache_raw_cmd


class Apalache:
    def __init__(self, stdin):
        self.stdin = stdin

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
        cmd = None
        if stdin:
            data = json.loads(self.stdin.read())
            cmd = RawCmd()
            cmd.mem = data["mem"]
            cmd.cleanup = data["cleanup"]
            cmd.cwd = data["cwd"]
            cmd.jar = data["jar"]
            cmd.args = ApalacheArgs(**data["args"])

        else:
            cmd = RawCmd()
            cmd.mem = mem
            cmd.cleanup = cleanup
            cmd.cwd = cwd
            cmd.jar = jar
            cmd.args = ApalacheArgs(
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

        result = exec_apalache_raw_cmd(cmd)
        stdout_pretty = result.process.stdout.decode("unicode_escape")
        stderr_pretty = result.process.stderr.decode("unicode_escape")

        print(
            f"""Ran 'apalache raw'.
shell cmd: {result.process.args}
return code: {result.process.returncode}
files: {result.files}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )

    def pure(self):
        assert self.stdin is not None
        data = json.loads(self.stdin.read())

        cmd = PureCmd()
        cmd.jar = data["jar"]
        cmd.args = ApalacheArgs(**data["args"])
        cmd.files = data["files"]

        result = exec_apalache_pure_cmd(cmd)

        print(result)
