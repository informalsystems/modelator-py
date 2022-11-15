import json as stdjson

from .pure import tlc_pure
from .raw import RawCmd, TlcArgs, tlc_raw


class Tlc:
    def __init__(self, stdin):
        self._stdin = stdin

    def pure(self):
        """
        Run TLC without side effects using json input data.

        Runs TLC in a temporary directory, writing all necessary data into the
        directory before calling TLC, and reading back all necessary results
        back into memory.

        Writes the result to stdout in json.

        Requires json input data on stdin (`<command> < data.json`).

        WARNING: does not support all CLI arguments in TLC 2.18
        """
        assert (
            self._stdin is not None
        ), "The pure interface requires json input in stdin"
        json_dict = stdjson.loads(self._stdin.read())

        result = tlc_pure(json=json_dict)
        to_print = stdjson.dumps(result, indent=4, sort_keys=True)
        print(to_print)

    def raw(
        self,
        *,
        json=False,
        cwd=None,
        jar=None,
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
        Run TLC without removing side effects (for debugging).

        Run TLC directly without creating a temporary directory. This is mainly
        useful for debugging. Arguments can be provided on command line or by
        specifying the --json flag and providing json on stdin (`<command> < data.json`).

        WARNING: does not support all CLI arguments in TLC 2.18

        Arguments:
            json : Read arguments from json instead of cli?
            cwd : Full path to directory to run TLC from.
            jar : Full path to TLC version 2.18 jar (other versions may work).
            aril : TLC argument, see `<tlc> --help`.
            checkpoint : TLC argument, see `<tlc> --help`.
            cleanup : TLC argument, see `<tlc> --help`.
            config : TLC argument, see `<tlc> --help`.
            cont : TLC argument, see `<tlc> --help`.
            coverage : TLC argument, see `<tlc> --help`.
            deadlock : TLC argument, see `<tlc> --help`.
            debug : TLC argument, see `<tlc> --help`.
            depth : TLC argument, see `<tlc> --help`.
            dfid : TLC argument, see `<tlc> --help`.
            difftrace : TLC argument, see `<tlc> --help`.
            dump : TLC argument, see `<tlc> --help`.
            fp : TLC argument, see `<tlc> --help`.
            fpbits : TLC argument, see `<tlc> --help`.
            fpmem : TLC argument, see `<tlc> --help`.
            generate_spec_te : TLC argument, see `<tlc> --help`.
            gzip : TLC argument, see `<tlc> --help`.
            h : TLC argument, see `<tlc> --help`.
            max_set_size : TLC argument, see `<tlc> --help`.
            metadir : TLC argument, see `<tlc> --help`.
            nowarning : TLC argument, see `<tlc> --help`.
            recover : TLC argument, see `<tlc> --help`.
            seed : TLC argument, see `<tlc> --help`.
            simulate : TLC argument, see `<tlc> --help`.
            terse : TLC argument, see `<tlc> --help`.
            tool : TLC argument, see `<tlc> --help`.
            userfile : TLC argument, see `<tlc> --help`.
            view : TLC argument, see `<tlc> --help`.
            workers : TLC argument, see `<tlc> --help`.
            file : TLC argument, see `<tlc> --help`.
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

        stdout_pretty = result.stdout.decode()
        stderr_pretty = result.stderr.decode()

        obj_to_print = {}
        obj_to_print["shell_cmd"] = result.args
        obj_to_print["return_code"] = result.returncode
        obj_to_print["stdout"] = stdout_pretty
        obj_to_print["stderr"] = stderr_pretty

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print)
