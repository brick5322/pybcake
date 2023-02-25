from abc import abstractmethod
import json
from copy import copy


class Generator:
    def __init__(self):
        self.options = []
        pass

    @abstractmethod
    def __call__(self, target, cmd: str = ""):
        return cmd

    def load_options(self, json_name: str, json_key: str = None):
        with open(json_name) as fjson:
            options = None
            if json_key is None:
                options = json.load(fjson)
            else:
                options = json.load(fjson)[json_key]

            keys = self.__dict__.keys() & options.keys()

            for i in keys:
                self.__dict__[i] += options[i]

        return self

    def __add__(self, options: dict):
        keys = self.__dict__.keys() & options.keys()

        for i in keys:
            assert isinstance(options[i], list)
            assert isinstance(self.__dict__[i], list)
            for value in options[i]:
                self.__dict__[i].insert(0, value)
        return self

    def __copy__(self):
        ret = self.__class__() 
        for k,v in self.__dict__.items():
            if isinstance(v,list):
                setattr(ret,k,copy(v))
            else:
                setattr(ret,k,v)
        return ret

