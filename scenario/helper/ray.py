import random

import psutil
import ray

from scenario.helper.scenario import get_zero_stats, get_zero_stats_variant
from simulator.constants.keys import nrun_key, nday_key, nvariant_key
from simulator.helper.plot import print_progress_bar
from scenario.helper.progressbar import ProgressBar


def launch_parallel_run(params, env_dic, fun, ncpu, progress_total_count):
    if ncpu < 0:
        num_cpus = max(psutil.cpu_count(logical=False) - ncpu, 1)
    elif ncpu == 0:
        num_cpus = 1
    else:
        num_cpus = min(ncpu, psutil.cpu_count(logical=False))
    ray.init(num_cpus=num_cpus)
    pb = ProgressBar(params[nrun_key] * progress_total_count)
    actor = pb.actor
    ray_params = ray.put(params)
    ray_env_dic = ray.put(env_dic)
    stats_l = []
    for run_id in range(params[nrun_key]):
        stats_l.append(fun.remote(ray_env_dic, ray_params, run_id, random.randint(0, 10000), actor))
    pb.print_until_done()
    return ray.get(stats_l)


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
