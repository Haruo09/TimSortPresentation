import numpy as np
from scipy.optimize import curve_fit
from benchmark_utils import (
    MIN_SIZE, MAX_SIZE, NUM_STEPS,
    benchmark_c_func, load_dynamic_lib, timsort_complexity_func,
    gen_random_array, gen_nearly_sorted_array, gen_reverse_sorted_array
)

# Standardized distribution generators
DISTRIBUTIONS = {
    "random": gen_random_array,
    "nearly_sorted": gen_nearly_sorted_array,
    "reverse_sorted": gen_reverse_sorted_array
}

def get_algorithm_func(algo_name):
    """Dynamically fetches the C function based on a string name."""
    c_lib = load_dynamic_lib()
    # Map CLI strings to C function names
    algo_map = {
        "timsort": c_lib.timSortAlgo,
        "bettertimsort": c_lib.betterTimSortAlgo,
        "quicksort": c_lib.quickSortAlgo,
        "betterquicksort": c_lib.betterQuickSortAlgo,
        "peaktimsort": c_lib.peakTimSortAlgo,
    }
    if algo_name not in algo_map:
        raise ValueError(f"Algorithm '{algo_name}' not found in shared library.")
    return algo_map[algo_name]

def run_single_complexity(algo_name):
    """Executes benchmarks and curve fitting for a single algorithm."""
    c_func = get_algorithm_func(algo_name)
    sizes = np.unique(np.geomspace(MIN_SIZE, MAX_SIZE, num=NUM_STEPS, dtype=int))
    
    results = {"sizes": sizes, "times": {}, "fits": {}}
    
    for dist_name, gen_func in DISTRIBUTIONS.items():
        times = benchmark_c_func(c_func, sizes, gen_func)
        p_opt, _ = curve_fit(timsort_complexity_func, sizes, times)
        
        results["times"][dist_name] = times
        results["fits"][dist_name] = p_opt

    return results

def run_comparison(algo1_name, algo2_name):
    """Executes benchmarks to compare two algorithms head-to-head."""
    func1 = get_algorithm_func(algo1_name)
    func2 = get_algorithm_func(algo2_name)
    sizes = np.unique(np.geomspace(MIN_SIZE, MAX_SIZE, num=NUM_STEPS, dtype=int))
    
    results = {"sizes": sizes, "algo1_times": {}, "algo2_times": {}}
    
    for dist_name, gen_func in DISTRIBUTIONS.items():
        results["algo1_times"][dist_name] = benchmark_c_func(func1, sizes, gen_func)
        results["algo2_times"][dist_name] = benchmark_c_func(func2, sizes, gen_func)

    return results
