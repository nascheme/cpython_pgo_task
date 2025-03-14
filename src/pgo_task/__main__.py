import sys
import glob
import importlib
import os
import time
import argparse
import dataclasses
import threading


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


def run_tasks(tasks, tasks_to_run, iterations, barrier=None):
    print('Running PGO tasks...')
    total_time = 0
    use_threads = barrier is not None
    for name in tasks_to_run:
        if barrier is not None:
            barrier.wait()
        task = tasks[name]
        module = importlib.import_module(f'pgo_task.{name}')
        if not hasattr(module, 'run_pgo'):
            print('task module missing run_pgo()', task.filename)
            continue
        if use_threads and not getattr(module, 'THREAD_SAFE', True):
            print('skipping non-thread safe task', task.name)
            continue
        t0 = time.perf_counter()
        if not use_threads:
            print(f'{name:>40}', end='', flush=True)
        for _ in range(iterations):
            module.run_pgo()
        tm = time.perf_counter() - t0
        total_time += tm
        if use_threads:
            print(f'{name:>40} {tm:.3f}s')
        else:
            print(f' {tm:.3f}s')
    if barrier is not None:
        barrier.wait()
    print(f'Total time for tasks {total_time:.3f} seconds')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        '--iterations',
        type=int,
        default=1,
        help='Number of iterations to run.',
    )
    parser.add_argument(
        '-t',
        '--threads',
        type=int,
        default=1,
        help='Number of threads to run.',
    )
    parser.add_argument('tasks', nargs='*', help='Name of tasks to run.')
    args = parser.parse_args()
    cmdline_tasks = set(args.tasks)
    tasks = find_tasks()
    if cmdline_tasks:
        tasks_to_run = cmdline_tasks
    else:
        tasks_to_run = sorted(tasks)
    if args.threads == 1:
        run_tasks(tasks, tasks_to_run, args.iterations)
    else:
        threads = []
        barrier = threading.Barrier(args.threads)
        for i in range(args.threads):

            def run():
                run_tasks(
                    tasks, tasks_to_run, args.iterations, barrier=barrier
                )

            threads.append(threading.Thread(target=run))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    main()
