This is a collection of scripts that is suitable to run as the CPython PGO
(profile-guided optimization) task.  The initial collection of scripts is
based on benchmarks from the `pyperformance` suite.

This collection might also be useful if you want to run a profiler and see
where execution time is spent while running the scripts.

Example usage:

    $ uv sync
    $ source .venv/bin/activate
    $ python -m pgo_task
    $ perf record python -X perf -m pgo_task -r 4
    $ perf report

You can run a subset of the scripts by listing their names as arguments:

    $ python -m pgo_task bm_chaos bm_go
