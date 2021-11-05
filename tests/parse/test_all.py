import modelator.parse.apalache as apalache


def test_parse_apalache_output_dir_name_from_stdout_str():
    s = """# If you have changed your mind, disable the statistics with config --enable-stats=false.

Output directory: /Users/john/Documents/mbt-python/tests/resource/apalache-out/2PossibleTracesTests.tla_2021-11-04T08-05-00_3883599675012555039
Checker options: filename=2PossibleTracesTests.tla, init=, next=, inv=IsThree I@08:05:00.355"""
    result = apalache.parse_apalache_output_dir_name_from_stdout_str(s)
    assert (
        result
        == "/Users/john/Documents/mbt-python/tests/resource/apalache-out/2PossibleTracesTests.tla_2021-11-04T08-05-00_3883599675012555039"
    )
