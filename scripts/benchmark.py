import ctypes
import os
import platform
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# =====================================================================
# CONFIGURATION PARAMETERS (Modify these as needed)
# =====================================================================
MIN_SIZE = 100
MAX_SIZE = 100_000
NUM_STEPS = 40  # Number of distinct array sizes to evaluate
TRIALS_PER_SIZE = 5  # Benchmark repetitions per array size
SWAP_NOISE_PERCENT = 0.05  # 5% random swaps for Nearly-Sorted arrays

# Output Plot File
OUTPUT_IMAGE_PATH = "docs/benchmark_results.png"


# =====================================================================
# C DYNAMIC LIBRARY LOADER
# =====================================================================
def load_timsort_lib():
    """Loads the compiled timsort dynamic library cross-platform."""
    system_name = platform.system()
    lib_ext = ".dll" if system_name == "Windows" else ".so"
    lib_filename = f"timsort{lib_ext}" if system_name == "Windows" else f"libtimsort{lib_ext}"
    
    lib_path = os.path.abspath(os.path.join("build", "lib", lib_filename))
    
    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"Could not find compiled dynamic library at '{lib_path}'. "
            "Please run 'make' before running this benchmark script."
        )

    c_lib = ctypes.CDLL(lib_path)
    
    # Define signature for timSortAlgo(int *arr, int n)
    c_lib.timSortAlgo.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
    ]
    c_lib.timSortAlgo.restype = None
    
    return c_lib


# =====================================================================
# THEORETICAL COMPLEXITY MODEL
# =====================================================================
def timsort_complexity_func(n, a, b):
    """Theoretical O(n log2 n) regression function."""
    return a * n * np.log2(n) + b


# =====================================================================
# DATA GENERATORS
# =====================================================================
def generate_random_array(n: int) -> np.ndarray:
    return np.random.randint(-1_000_000, 1_000_000, size=n, dtype=np.int32)


def generate_nearly_sorted_array(n: int, swap_ratio: float = SWAP_NOISE_PERCENT) -> np.ndarray:
    arr = np.arange(n, dtype=np.int32)
    num_swaps = max(1, int(n * swap_ratio))
    for _ in range(num_swaps):
        idx1, idx2 = np.random.randint(0, n, size=2)
        arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
    return arr


def generate_reverse_sorted_array(n: int) -> np.ndarray:
    return np.arange(n, 0, -1, dtype=np.int32)


# =====================================================================
# BENCHMARK ENGINE
# =====================================================================
def benchmark_algorithm(c_lib, sizes, dist_func):
    """Measures median execution time for a given distribution across array sizes."""
    median_times = []

    for size in sizes:
        trial_times = []
        base_array = dist_func(size)

        for _ in range(TRIALS_PER_SIZE):
            # Create a fresh copy to prevent sorting an already-sorted array in-place
            test_arr = base_array.copy()
            c_arr = test_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

            start_time = time.perf_counter()
            c_lib.timSortAlgo(c_arr, ctypes.c_int(size))
            end_time = time.perf_counter()

            trial_times.append(end_time - start_time)

        # Record median trial duration
        median_times.append(np.median(trial_times))

    return np.array(median_times)


def main():
    print("Loading C TimSort shared library...")
    c_lib = load_timsort_lib()

    # Generate log-spaced array sizes for even distribution density
    sizes = np.geomspace(MIN_SIZE, MAX_SIZE, num=NUM_STEPS, dtype=int)
    sizes = np.unique(sizes)  # Remove any potential duplicates

    print(f"Running benchmarks on {len(sizes)} array sizes ranging from {sizes[0]} to {sizes[-1]}...")
    
    # 1. Run Benchmarks
    print(" Benchmarking Random arrays...")
    times_random = benchmark_algorithm(c_lib, sizes, generate_random_array)

    print(" Benchmarking Nearly-Sorted arrays...")
    times_nearly = benchmark_algorithm(c_lib, sizes, generate_nearly_sorted_array)

    print(" Benchmarking Reverse-Sorted arrays...")
    times_reverse = benchmark_algorithm(c_lib, sizes, generate_reverse_sorted_array)

    # 2. Curve Fitting
    print("Fitting theoretical O(n log2 n) curves...")
    
    p_rand, _ = curve_fit(timsort_complexity_func, sizes, times_random)
    p_near, _ = curve_fit(timsort_complexity_func, sizes, times_nearly)
    p_rev, _ = curve_fit(timsort_complexity_func, sizes, times_reverse)

    fit_sizes = np.linspace(sizes[0], sizes[-1], 200)
    fit_rand = timsort_complexity_func(fit_sizes, *p_rand)
    fit_near = timsort_complexity_func(fit_sizes, *p_near)
    fit_rev = timsort_complexity_func(fit_sizes, *p_rev)

    # 3. Plotting Results (2x2 Grid)
    print("Generating performance plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("TimSort (C Implementation) Empirical Complexity Analysis", fontsize=16)

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
    axes[0, 1].set_title(f"Nearly-Sorted Input Array ({int(SWAP_NOISE_PERCENT*100)}% Noise)")
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

    # Plot 4: Combined Average & Comparative Trends
    axes[1, 1].plot(sizes, times_random, label="Random", color='crimson', linestyle='--')
    axes[1, 1].plot(sizes, times_nearly, label="Nearly-Sorted", color='darkgreen', linestyle='-.')
    axes[1, 1].plot(sizes, times_reverse, label="Reverse-Sorted", color='purple', linestyle=':')
    
    avg_times = (times_random + times_nearly + times_reverse) / 3.0
    axes[1, 1].plot(sizes, avg_times, label="Average Across All Cases", color='black', linewidth=2)

    axes[1, 1].set_title("Comparative Distribution Performance")
    axes[1, 1].set_xlabel("Array Size (n)")
    axes[1, 1].set_ylabel("Execution Time (seconds)")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=300)
    print(f"\nPlot successfully saved to '{OUTPUT_IMAGE_PATH}'!")
    plt.show(block=False)
    plt.pause(1)
    input("\nPress Enter to exit")
    plt.close()


if __name__ == "__main__":
    main()
