from .generator import Generator
import os
from concurrent.futures import ThreadPoolExecutor


class Target:
    def __init__(self, name: str):
        self.name = name
        self.sources = []
        self.command = None
        self.generate = Generator()
        self.dependency = []

    def make(self, nb_thread: int = 1, thr_pool: ThreadPoolExecutor = None):
        if thr_pool is None:
            thr_pool = ThreadPoolExecutor(max_workers=nb_thread)

        dependency_targets = []
        for deps in self.dependency:
            dependency_targets += deps.make(thr_pool=thr_pool)

        sources = []
        for src in self.sources:
            if not isinstance(src, str):
                sources += src.make(thr_pool=thr_pool)
            else:
                sources.append(src)

        self.sources = sources

        if target_is_latest(self.name, sources + dependency_targets):
            return [self.name]
        cmd = self.generate(target=self)

        try:
            os.makedirs(os.path.split(self.name)[0])
        except OSError:
            pass

        print(cmd)

        thr_pool.submit(os.system, cmd).result()

        return [self.name]


def target_is_latest(target_file: str, dependency: list) -> bool:
    if not os.path.exists(target_file):
        return False

    target_mtime = os.path.getmtime(target_file)
    for dependency_file in dependency:
        if not os.path.exists(dependency_file):
            return False
        if os.path.getmtime(dependency_file) > target_mtime:
            return False

    return True
