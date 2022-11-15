import json as stdjson

from .pure import apalache_pure
from .raw import ApalacheArgs, RawCmd, apalache_raw


class Apalache:
    def __init__(self, stdin):
        self._stdin = stdin

    def pure(self):
        """
        Run Apalache without side effects using json input data.

        Runs Apalache in a temporary directory, writing all necessary data into the
        directory before calling Apalache, and reading back all necessary results
        back into memory.

        Writes the result to stdout in json.

        Requires json input data on stdin (`<command> < data.json`).
        """
        assert (
            self._stdin is not None
        ), "The pure interface requires json input in stdin"
        json_dict = stdjson.loads(self._stdin.read())

        result = apalache_pure(json=json_dict)
        to_print = stdjson.dumps(result, indent=4, sort_keys=True)
        print(to_print)

    def raw(
        self,
        *,
        json=None,
        cwd=None,
        jar=None,
        cmd=None,
        file=None,
        config_file=None,
        debug=None,
        out_dir=None,
        profiling=None,
        run_dir=None,
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
        no_deadlock=None,
        nworkers=None,
        smt_encoding=None,
        tuning=None,
        tuning_options=None,
        view=None,
        enable_stats=None,
        before=None,
        action=None,
        assertion=None,
        next=None,
        infer_poly=None,
        output=None,
        features=None,
    ):
        """
        Run Apalache without removing side effects (for debugging).

        Run Apalache directly without creating a temporary directory. This is mainly
        useful for debugging. Arguments can be provided on command line or by
        specifying the --json flag and providing json on stdin (`<command> < data.json`).

        Arguments:
            json : Read arguments from json instead of cli?
            cwd : Full path to directory to run Apalache from.
            jar : Full path to Apalache version 0.23.0 jar (other versions may work).
            cmd : Apalache argument, see `<apalache> --help`.
            file : Apalache argument, see `<apalache> --help`.
            config_file : Apalache argument, see `<apalache> --help`.
            debug : Apalache argument, see `<apalache> --help`.
            out_dir : Apalache argument, see `<apalache> --help`.
            profiling : Apalache argument, see `<apalache> --help`.
            run_dir : Apalache argument, see `<apalache> --help`.
            smtprof : Apalache argument, see `<apalache> --help`.
            write_intermediate : Apalache argument, see `<apalache> --help`.
            algo : Apalache argument, see `<apalache> --help`.
            cinit : Apalache argument, see `<apalache> --help`.
            config : Apalache argument, see `<apalache> --help`.
            discard_disabled : Apalache argument, see `<apalache> --help`.
            init : Apalache argument, see `<apalache> --help`.
            inv : Apalache argument, see `<apalache> --help`.
            length : Apalache argument, see `<apalache> --help`.
            max_error : Apalache argument, see `<apalache> --help`.
            no_deadlock : Apalache argument, see `<apalache> --help`.
            nworkers : Apalache argument, see `<apalache> --help`.
            smt_encoding : Apalache argument, see `<apalache> --help`.
            tuning : Apalache argument, see `<apalache> --help`.
            tuning_options : Apalache argument, see `<apalache> --help`.
            view : Apalache argument, see `<apalache> --help`.
            enable_stats : Apalache argument, see `<apalache> --help`.
            before : Apalache argument, see `<apalache> --help`.
            action : Apalache argument, see `<apalache> --help`.
            assertion : Apalache argument, see `<apalache> --help`.
            next : Apalache argument, see `<apalache> --help`.
            infer_poly : Apalache argument, see `<apalache> --help`.
            output : Apalache argument, see `<apalache> --help`.
            features : Apalache argument, see `<apalache> --help`.
        """
        result = None
        if json:
            json_dict = stdjson.loads(self._stdin.read())
            result = apalache_raw(json=json_dict)
        else:
            raw_cmd = RawCmd()
            raw_cmd.cwd = cwd
            raw_cmd.jar = jar
            raw_cmd.args = ApalacheArgs(
                cmd,
                file,
                config_file,
                debug,
                out_dir,
                profiling,
                run_dir,
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
                no_deadlock,
                nworkers,
                smt_encoding,
                tuning,
                tuning_options,
                view,
                enable_stats,
                before,
                action,
                assertion,
                next,
                infer_poly,
                output,
                features,
            )

            result = apalache_raw(cmd=raw_cmd)

        stdout_pretty = result.stdout.decode()
        stderr_pretty = result.stderr.decode()

        obj_to_print = {}
        obj_to_print["shell_cmd"] = result.args
        obj_to_print["return_code"] = result.returncode
        obj_to_print["stdout"] = stdout_pretty
        obj_to_print["stderr"] = stderr_pretty

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print)
