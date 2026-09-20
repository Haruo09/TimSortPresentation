import os
import matplotlib.pyplot as plt
import numpy as np

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
)

OUTPUT_IMAGE_PATH = "docs/timsort_vs_betterquicksort.png"


def main():
    c_lib = load_dynamic_lib()
    sizes = np.geomspace(MIN_SIZE, MAX_SIZE, num=NUM_STEPS, dtype=int)
    sizes = np.unique(sizes)

    dists = [
        ("Totally Random Array", gen_random_array),
        (f"Nearly-Sorted Array ({SWAP_NOISE_PERCENT*100}% Noise)", gen_nearly_sorted_array),
        ("Reverse-Sorted Array", gen_reverse_sorted_array),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Performance Comparison: TimSort vs Better QuickSort (C Code)", fontsize=15)

    for i, (title, dist_gen) in enumerate(dists):
        print(f" -> Benchmarking: {title}...")
        ts_times = benchmark_c_func(c_lib.timSortAlgo, sizes, dist_gen)
        qs_times = benchmark_c_func(c_lib.betterQuickSortAlgo, sizes, dist_gen)

        axes[i].plot(sizes, ts_times, label="TimSort", color="crimson", linewidth=2)
        axes[i].plot(sizes, qs_times, label="BetterQuickSort", color="royalblue", linewidth=2, linestyle="--")

        axes[i].set_title(title)
        axes[i].set_xlabel("Array Size (n)")
        axes[i].set_ylabel("Execution Time (seconds)")
        axes[i].legend()
        axes[i].grid(True)

    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=300)
    print(f"Saved comparison plot to '{OUTPUT_IMAGE_PATH}'.")
    plt.show()


if __name__ == "__main__":
    main()
