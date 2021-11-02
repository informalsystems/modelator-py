import fire


class Modelator(object):
    def apalache(self, name):
        print(name)

    def tlc(self):
        raise Exception("noimpl")


if __name__ == "__main__":
    fire.Fire(Modelator)
