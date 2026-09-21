import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from benchmark_utils import (
    MIN_SIZE,
    MAX_SIZE,
    NUM_STEPS,
    SWAP_NOISE_PERCENT,
    benchmark_c_func,
    gen_nearly_sorted_array,
    gen_random_array,
    gen_reverse_sorted_array,
    load_dynamic_lib,
    timsort_complexity_func,
)

OUTPUT_IMAGE_PATH = "docs/bettertimsort_benchmark.png"


def main():
    print("Loading C TimSort shared library...")
    c_lib = load_dynamic_lib()

    sizes = np.geomspace(MIN_SIZE, MAX_SIZE, num=NUM_STEPS, dtype=int)
    sizes = np.unique(sizes)

    print("Running TimSort empirical complexity benchmarks...")
    times_random = benchmark_c_func(c_lib.betterTimSortAlgo, sizes, gen_random_array)
    times_nearly = benchmark_c_func(c_lib.betterTimSortAlgo, sizes, gen_nearly_sorted_array)
    times_reverse = benchmark_c_func(c_lib.betterTimSortAlgo, sizes, gen_reverse_sorted_array)

    print("Fitting theoretical O(n log2 n) curves...")
    p_rand, _ = curve_fit(timsort_complexity_func, sizes, times_random)
    p_near, _ = curve_fit(timsort_complexity_func, sizes, times_nearly)
    p_rev, _ = curve_fit(timsort_complexity_func, sizes, times_reverse)

    fit_sizes = np.linspace(sizes[0], sizes[-1], 200)
    fit_rand = timsort_complexity_func(fit_sizes, *p_rand)
    fit_near = timsort_complexity_func(fit_sizes, *p_near)
    fit_rev = timsort_complexity_func(fit_sizes, *p_rev)

    print("Generating plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("BetterTimSort (C Implementation) Empirical Complexity Analysis", fontsize=16)

    # Plot 1: Random
    axes[0, 0].scatter(sizes, times_random, color='crimson', label="Measured Data", s=20)
    axes[0, 0].plot(fit_sizes, fit_rand, color='darkblue', label=f"Fit: y = {p_rand[0]:.2e}·n·log₂(n) + {p_rand[1]:.2e}")
    axes[0, 0].set_title("Random Input Array")
    axes[0, 0].set_xlabel("Array Size (n)")
    axes[0, 0].set_ylabel("Execution Time (seconds)")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Plot 2: Nearly-Sorted
    axes[0, 1].scatter(sizes, times_nearly, color='darkgreen', label="Measured Data", s=20)
    axes[0, 1].plot(fit_sizes, fit_near, color='teal', label=f"Fit: y = {p_near[0]:.2e}·n·log₂(n) + {p_near[1]:.2e}")
    axes[0, 1].set_title(f"Nearly-Sorted Input Array ({SWAP_NOISE_PERCENT*100}% Noise)")
    axes[0, 1].set_xlabel("Array Size (n)")
    axes[0, 1].set_ylabel("Execution Time (seconds)")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Plot 3: Reverse-Sorted
    axes[1, 0].scatter(sizes, times_reverse, color='purple', label="Measured Data", s=20)
    axes[1, 0].plot(fit_sizes, fit_rev, color='indigo', label=f"Fit: y = {p_rev[0]:.2e}·n·log₂(n) + {p_rev[1]:.2e}")
    axes[1, 0].set_title("Reverse-Sorted Input Array")
    axes[1, 0].set_xlabel("Array Size (n)")
    axes[1, 0].set_ylabel("Execution Time (seconds)")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # Plot 4: Combined Average Trends
    axes[1, 1].plot(fit_sizes, fit_rand, label="Random", color='crimson', linestyle='--')
    axes[1, 1].plot(fit_sizes, fit_near, label="Nearly-Sorted", color='darkgreen', linestyle='-.')
    axes[1, 1].plot(fit_sizes, fit_rev, label="Reverse-Sorted", color='purple', linestyle=':')
    avg_fit = (fit_rand + fit_near + fit_rev) / 3.0
    axes[1, 1].plot(fit_sizes, avg_fit, label="Average Across All Cases", color='black', linewidth=2)

    axes[1, 1].set_title("Comparative Distribution Performance")
    axes[1, 1].set_xlabel("Array Size (n)")
    axes[1, 1].set_ylabel("Execution Time (seconds)")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=300)
    print(f"Saved plot to '{OUTPUT_IMAGE_PATH}'.")
    plt.show()


if __name__ == "__main__":
    main()

