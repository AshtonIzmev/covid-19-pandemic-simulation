import random

import psutil
import ray

from scenario.helper.progressbar import ProgressBar
from scenario.helper.scenario import get_zero_stats, get_zero_stats_variant
from simulator.constants.keys import nday_key, nrun_key, nvariant_key
from simulator.helper.plot import print_progress_bar


def resolve_num_cpus(ncpu):
    """--ncpu N uses N cores, 0 uses one, and -N leaves N cores free.

    The negative branch used to *subtract* a negative number, so `--ncpu -1`
    asked ray for one core more than the machine has instead of one less.
    """
    available = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
    if ncpu < 0:
        return max(available + ncpu, 1)
    if ncpu == 0:
        return 1
    return max(min(ncpu, available), 1)


def launch_parallel_run(params, env_dic, fun, ncpu, progress_total_count):
    already_running = ray.is_initialized()
    if not already_running:
        ray.init(num_cpus=resolve_num_cpus(ncpu))
    try:
        pb = ProgressBar(params[nrun_key] * progress_total_count)
        actor = pb.actor
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        stats_l = [fun.remote(ray_env_dic, ray_params, run_id, random.randint(0, 10000), actor)
                   for run_id in range(params[nrun_key])]
        pb.print_until_done()
        return ray.get(stats_l)
    finally:
        if not already_running:
            ray.shutdown()


def launch_parallel_byday(params, env_dic, fun, ncpu):
    stats_all = launch_parallel_run(params, env_dic, fun, ncpu, params[nday_key])
    stats = get_zero_stats(params)
    for run_id, run_stats in stats_all:
        merge_run_stat(stats, run_stats, run_id)
    return stats


def launch_parallel_byvariant(params, env_dic, fun, ncpu):
    stats_all = launch_parallel_run(params, env_dic, fun, ncpu, params[nday_key]*params[nvariant_key])
    stats = get_zero_stats_variant(params)
    for run_id, run_stats in stats_all:
        merge_run_stat(stats, run_stats, run_id)
    return stats


def launch_run(params, env_dic, fun, display_progress=True):
    stats = get_zero_stats(params)
    stats_l = []
    for run_id in range(params[nrun_key]):
        if display_progress:
            print_progress_bar(run_id, params[nrun_key], prefix='Progress:', suffix='Complete', length=50)
        stats_l.append(fun(env_dic, params, run_id))
    for run_id, run_stats in stats_l:
        merge_run_stat(stats, run_stats, run_id)
    return stats


def merge_run_stat(stats, run_stats_arg, run_arg):
    for k, v in run_stats_arg.items():
        stats[k][run_arg] = v
