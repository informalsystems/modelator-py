import json
import os
import tempfile

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
            data = {
                "mem": data["mem"],
                "cleanup": data["cleanup"],
                "cwd": data["cwd"],
                "jar": data["jar"],
                "args": ApalacheArgs(**data["args"]),
            }
            cmd = RawCmd(**data)

        else:
            args = ApalacheArgs(
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
            cmd = RawCmd(mem, cleanup, cwd, jar, args)
        result = exec_apalache_raw_cmd(cmd)
        stdout_pretty = result.stdout.decode("unicode_escape")
        stderr_pretty = result.stderr.decode("unicode_escape")

        print(
            f"""Ran 'apalache raw'.
shell cmd: {result.args}
return code: {result.returncode}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )

    def pure(self):
        assert self.stdin is not None
        data = json.loads(self.stdin.read())

        raw_cmd = RawCmd()
        raw_cmd.args = ApalacheArgs(**data["args"])
        raw_cmd.jar = data["jar"]
        raw_cmd.mem = True
        raw_cmd.cleanup = True

        with tempfile.TemporaryDirectory(
            prefix="mbt-python-apalache-temp-dir-"
        ) as dirname:
            raw_cmd.cwd = dirname
            for filename, file_content_str in data["files"].items():
                full_path = os.path.join(dirname, filename)
                with open(full_path, "w") as fd:
                    fd.write(file_content_str)

                # TODO: delete this debug write and make a permanent solution
                with open(
                    os.path.join(
                        os.path.expanduser("~/Documents/work/mbt-python/tempme"),
                        filename,
                    ),
                    "w",
                ) as fd:
                    fd.write(file_content_str)

            return exec_apalache_raw_cmd(raw_cmd)
