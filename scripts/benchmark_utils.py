import ctypes
import os
import platform
import time
import numpy as np

# Default Benchmark Settings
MIN_SIZE = 100
MAX_SIZE = 10_000_000
NUM_STEPS = 30
TRIALS_PER_SIZE = 10 
SWAP_NOISE_PERCENT = 0.05


def load_dynamic_lib():
    """Loads the compiled timsort/quicksort dynamic library cross-platform."""
    system_name = platform.system()
    lib_ext = ".dll" if system_name == "Windows" else ".so"
    lib_filename = f"timsort{lib_ext}" if system_name == "Windows" else f"libtimsort{lib_ext}"
    lib_path = os.path.abspath(os.path.join("build", "lib", lib_filename))

    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"Could not find compiled dynamic library at '{lib_path}'. "
            "Please run 'make' before running benchmark scripts."
        )

    c_lib = ctypes.CDLL(lib_path)

    # Configure signatures if exported symbols are present
    if hasattr(c_lib, "timSortAlgo"):
        c_lib.timSortAlgo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        c_lib.timSortAlgo.restype = None

    if hasattr(c_lib, "quickSortAlgo"):
        c_lib.quickSortAlgo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        c_lib.quickSortAlgo.restype = None

    if hasattr(c_lib, "betterQuickSortAlgo"):
        c_lib.betterQuickSortAlgo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        c_lib.betterQuickSortAlgo.restype = None

    if hasattr(c_lib, "betterTimSortAlgo"):
        c_lib.betterTimSortAlgo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        c_lib.betterTimSortAlgo.restype = None

    if hasattr(c_lib, "peakTimSortAlgo"):
        c_lib.peakTimSortAlgo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        c_lib.peakTimSortAlgo.restype = None

    return c_lib


def gen_random_array(n: int) -> np.ndarray:
    """Generates an array filled with random 32-bit integers."""
    return np.random.randint(-1_000_000, 1_000_000, size=n, dtype=np.int32)

def gen_nearly_sorted_array(n: int, swap_ratio: float = SWAP_NOISE_PERCENT) -> np.ndarray:
    arr = np.arange(n, dtype=np.int32)
    num_swaps = max(1, int(n * swap_ratio))
    for _ in range(num_swaps):
        idx = np.random.randint(0, n - 1)
        arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
    return arr

# def gen_nearly_sorted_array(n: int, swap_ratio: float = SWAP_NOISE_PERCENT) -> np.ndarray:
#     """Generates a sorted array with a small percentage of random element swaps."""
#     arr = np.arange(n, dtype=np.int32)
#     num_swaps = max(1, int(n * swap_ratio))
#     for _ in range(num_swaps):
#         idx1, idx2 = np.random.randint(0, n, size=2)
#         arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
#     return arr


def gen_reverse_sorted_array(n: int) -> np.ndarray:
    """Generates a reverse-sorted array."""
    return np.arange(n, 0, -1, dtype=np.int32)


def benchmark_c_func(c_func, sizes, dist_gen, trials: int = TRIALS_PER_SIZE) -> np.ndarray:
    """Executes time benchmarks for a given C function across array sizes and returns median times."""
    median_times = []

    for size in sizes:
        base_array = dist_gen(size)
        trial_times = []

        for _ in range(trials):
            # Create a fresh copy to prevent sorting an already-sorted array in-place
            test_arr = base_array.copy()
            c_arr = test_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

            start_time = time.perf_counter()
            c_func(c_arr, ctypes.c_int(size))
            end_time = time.perf_counter()

            trial_times.append(end_time - start_time)

        median = np.median(trial_times)
        median_times.append(median)
        print(f" -> Time spent: {median}")

    return np.array(median_times)


def timsort_complexity_func(n, a, b):
    """Theoretical O(n log2 n) regression function."""
    return a * n * np.log2(n) + b
