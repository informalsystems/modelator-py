def parse_apalache_output_dir_name_from_stdout_str(s):
    """
    Try to parse the name of the output directory that Apalache uses

    s like:
    ...
    #
    # Usage statistics is ON. Thank you!
    # If you have changed your mind, disable the statistics with config --enable-stats=false.

    Output directory: /Users/john/Documents/mbt-python/tests/resource/apalache-out/2PossibleTracesTests.tla_2021-11-04T08-05-00_3883599675012555039
    Checker options: filename=2PossibleTracesTests.tla, init=, next=, inv=IsThree I@08:05:00.355
    ...
    """
    match = "Output directory: "
    ix = s.find(match)
    if ix == -1:
        raise Exception(
            f"Could not parse name of Apalache output directory from stdout string (Could not find '{match}' substr)"
        )
    # https://docs.python.org/3/library/stdtypes.html#str.partition
    partition = s[ix:].partition("\n")
    return partition[0][len(match) :]
