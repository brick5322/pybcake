import os

from .generator import Generator
from concurrent.futures import ThreadPoolExecutor, wait
from .target import Target, target_is_latest


class Group:
    def __init__(self, group_name: str = ""):
        self.group_name = group_name
        self.targets = []
        self.pre_generate = []
        self.post_generate = []
        self.dependency = []

    def make(self, nb_thread: int = 1, thr_pool: ThreadPoolExecutor = None):
        if thr_pool is None:
            thr_pool = ThreadPoolExecutor(max_workers=nb_thread)

        tasks = []

        for target in self.targets:
            dep_targets = []
            for dep in target.dependency:
                dep_targets += dep.make(thr_pool=thr_pool)

            for generate in self.pre_generate:
                generate(target=target)

            self.pre_generate = []

            sources = []

            for src in target.sources:
                if not isinstance(src, str):
                    assert isinstance(src, Target) or isinstance(src, Group)
                    sources += src.make(thr_pool=thr_pool)
                else:
                    sources.append(src)

            target.sources = sources

            if target_is_latest(target.name, sources + dep_targets + target.dep_files):
                continue

            cmd = target.generate(target=target)

            try:
                os.makedirs(os.path.split(target.name)[0])
            except OSError:
                pass

            for generate in self.post_generate:
                cmd = generate(target, cmd)

            print(cmd)
            tasks.append(thr_pool.submit(os.system, cmd))

        for task in tasks:
            task.result()

        return [i.name for i in self.targets]
