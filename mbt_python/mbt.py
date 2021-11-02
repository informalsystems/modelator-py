import json

import fire


class Hello(object):
    def explicit(self, foo, bar):
        print(f"Hello {foo} {bar}")

    def json(self, json_data_str):
        print(f"{json_data_str=}")
        json.loads(json_data_str)

    def json_file(self, json_file_path):
        print(f"{json_file_path=}")
        pass


class Modelator(object):
    def apalache(self):
        raise Exception("noimpl")

    def tlc(self):
        raise Exception("noimpl")


if __name__ == "__main__":
    fire.Fire({"hello": Hello})
