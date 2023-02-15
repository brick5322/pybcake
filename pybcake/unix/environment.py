import os


class Environment:
    def __init__(self, **kwargs):
        self.env = {}
        for k, v in kwargs.items():
            if isinstance(v, (list, tuple)) and v:
                value = ":"
                for s in v:
                    if v[0] == ":":
                        value += s
                    else:
                        value += ":" + s
                self.env[k] = value
            elif isinstance(v, str):
                if v[0] == ":":
                    self.env[k] = v
                else:
                    self.env[k] = ":" + v

    def run(self, cmd: str):
        for k, v in self.env.items():
            try:
                os.environ[k] += v
            except KeyError:
                os.environ[k] = v[1:]
        return os.system(cmd)

    def dump(self, shname: str, cmd: str):
        with open(shname, "w") as fp:
            for k, v in self.env.items():
                fp.write("export " + k + "=$" + k + v + "\n")
            fp.write(cmd + "\n")
