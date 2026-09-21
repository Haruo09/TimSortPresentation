import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from scripts.benchmark_utils import load_dynamic_lib

# Number of Hypothesis test cases generated per distribution per algorithm
N_EXAMPLES = 1_000

# Available algorithms to test in the dynamic library
TESTED_ALGORITHMS = [
    "timSortAlgo",
    "quickSortAlgo",
    "betterQuickSortAlgo",
    "betterTimSortAlgo",
]


@pytest.fixture(scope="module")
def c_lib():
    """Loads the dynamic library once for the entire module."""
    return load_dynamic_lib()


# =====================================================================
# 1. CUSTOM HYPOTHESIS STRATEGIES (COMPOSITE GENERATORS)
# =====================================================================

@st.composite
def random_arrays(draw, min_size=0, max_size=100_000):
    """Generates arbitrary 32-bit integer arrays with random lengths and values."""
    elements = draw(
        st.lists(
            st.integers(min_value=-2_147_483_648, max_value=2_147_483_647),
            min_size=min_size,
            max_size=max_size,
        )
    )
    return np.array(elements, dtype=np.int32)


@st.composite
def nearly_sorted_arrays(draw, min_size=0, max_size=100_000, max_noise_ratio=0.05):
    """Generates sorted arrays with up to max_noise_ratio randomly swapped element pairs."""
    arr = draw(random_arrays(min_size=min_size, max_size=max_size))
    arr.sort()  # Baseline sorted state
    n = len(arr)

    if n > 1:
        num_swaps = draw(
            st.integers(min_value=0, max_value=max(1, int(n * max_noise_ratio)))
        )
        for _ in range(num_swaps):
            i = draw(st.integers(min_value=0, max_value=n - 1))
            j = draw(st.integers(min_value=0, max_value=n - 1))
            arr[i], arr[j] = arr[j], arr[i]

    return arr


@st.composite
def reverse_sorted_arrays(draw, min_size=0, max_size=100_000):
    """Generates strictly descending arrays."""
    arr = draw(random_arrays(min_size=min_size, max_size=max_size))
    arr.sort()
    return np.ascontiguousarray(arr[::-1])


# =====================================================================
# 2. SHARED TEST ASSERTION HARNESS
# =====================================================================

def assert_sorting_correctness(c_lib, algo_name: str, raw_array: np.ndarray, dist_name: str):
    """Encapsulates memory pointer extraction, execution, and ground-truth verification."""
    if not hasattr(c_lib, algo_name):
        pytest.skip(f"Algorithm '{algo_name}' not available in compiled shared library.")

    c_func = getattr(c_lib, algo_name)
    expected = np.sort(raw_array)

    test_arr = raw_array.copy()
    c_arr = test_arr.ctypes.data_as(c_func.argtypes[0])

    c_func(c_arr, len(test_arr))

    np.testing.assert_array_equal(
        test_arr,
        expected,
        err_msg=(
            f"\nAlgorithm: {algo_name}"
            f"\nDistribution: {dist_name}"
            f"\nArray Length: {len(raw_array)}"
            f"\nFailing Input Array: {raw_array[:10]}... (truncated)"
        ),
    )


# =====================================================================
# 3. PROPERTY-BASED TEST SUITES
# =====================================================================

@pytest.mark.parametrize("algo_name", TESTED_ALGORITHMS)
@settings(
    max_examples=N_EXAMPLES,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(raw_array=random_arrays())
def test_random_array_property(c_lib, algo_name, raw_array):
    """Property test across N_EXAMPLES of totally random integer arrays."""
    assert_sorting_correctness(c_lib, algo_name, raw_array, "Totally Random")


@pytest.mark.parametrize("algo_name", TESTED_ALGORITHMS)
@settings(
    max_examples=N_EXAMPLES,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(raw_array=nearly_sorted_arrays())
def test_nearly_sorted_array_property(c_lib, algo_name, raw_array):
    """Property test across N_EXAMPLES of nearly-sorted integer arrays."""
    assert_sorting_correctness(c_lib, algo_name, raw_array, "Nearly Sorted")


@pytest.mark.parametrize("algo_name", TESTED_ALGORITHMS)
@settings(
    max_examples=N_EXAMPLES,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(raw_array=reverse_sorted_arrays())
def test_reverse_sorted_array_property(c_lib, algo_name, raw_array):
    """Property test across N_EXAMPLES of reverse-sorted integer arrays."""
    assert_sorting_correctness(c_lib, algo_name, raw_array, "Reverse Sorted")
