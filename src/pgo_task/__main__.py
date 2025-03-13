import sys
import glob
import importlib
import os
import time
import argparse
import dataclasses


@dataclasses.dataclass
class Task:
    name: str
    filename: str


def find_tasks():
    tasks = {}
    package_dir = os.path.dirname(__file__)
    for fn in glob.glob(os.path.join(package_dir, 'bm_*.py')):
        name, ext = os.path.splitext(os.path.basename(fn))
        tasks[name] = Task(name=name, filename=fn)
    return tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        '--iterations',
        type=int,
        default=1,
        help='Number of iterations to run.',
    )
    parser.add_argument('tasks', nargs='*', help='Name of tasks to run.')
    args = parser.parse_args()
    cmdline_tasks = set(args.tasks)
    total_time = 0
    tasks = find_tasks()
    if cmdline_tasks:
        tasks_to_run = cmdline_tasks
    else:
        tasks_to_run = sorted(tasks)
    print('Running PGO tasks...')
    for name in tasks_to_run:
        task = tasks[name]
        module = importlib.import_module(f'pgo_task.{name}')
        if not hasattr(module, 'run_pgo'):
            print('task module missing run_pgo()', task.filename)
            continue
        t0 = time.perf_counter()
        print(f'{name:>40}', end='', flush=True)
        for _ in range(args.iterations):
            module.run_pgo()
        tm = time.perf_counter() - t0
        total_time += tm
        print(f' {tm:.3f}s')
    print(f'Total time for tasks {total_time:.3f} seconds')


if __name__ == '__main__':
    main()
