import os
import matplotlib.pyplot as plt
import numpy as np
from benchmark_utils import SWAP_NOISE_PERCENT, timsort_complexity_func

DIST_TITLES = {
    "random": "Random Input Array",
    "nearly_sorted": f"Nearly-Sorted Array ({SWAP_NOISE_PERCENT*100}% Noise)",
    "reverse_sorted": "Reverse-Sorted Input Array"
}

def plot_complexity(algo_name, results, output_path):
    """Generates the 2x2 grid for single algorithm complexity analysis."""
    sizes = results["sizes"]
    fit_sizes = np.linspace(sizes[0], sizes[-1], 200)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"{algo_name.capitalize()} Empirical Complexity Analysis", fontsize=16)

    plot_configs = [
        ("random", 0, 0, 'crimson', 'darkblue'),
        ("nearly_sorted", 0, 1, 'darkgreen', 'teal'),
        ("reverse_sorted", 1, 0, 'purple', 'indigo')
    ]

    fit_lines = []

    for dist, row, col, scatter_color, fit_color in plot_configs:
        times = results["times"][dist]
        p_opt = results["fits"][dist]
        fit_y = timsort_complexity_func(fit_sizes, *p_opt)
        fit_lines.append(fit_y)

        ax = axes[row, col]
        ax.scatter(sizes, times, color=scatter_color, label="Measured Data", s=20)
        ax.plot(fit_sizes, fit_y, color=fit_color, label=f"Fit: y = {p_opt[0]:.2e}·n·log₂(n) + {p_opt[1]:.2e}")
        ax.set_title(DIST_TITLES[dist])
        ax.set_xlabel("Array Size (n)")
        ax.set_ylabel("Execution Time (seconds)")
        ax.legend()
        ax.grid(True)

    # Plot 4: Combined Averages
    ax = axes[1, 1]
    ax.plot(fit_sizes, fit_lines[0], label="Random", color='crimson', linestyle='--')
    ax.plot(fit_sizes, fit_lines[1], label="Nearly-Sorted", color='darkgreen', linestyle='-.')
    ax.plot(fit_sizes, fit_lines[2], label="Reverse-Sorted", color='purple', linestyle=':')
    
    avg_fit = sum(fit_lines) / 3.0
    ax.plot(fit_sizes, avg_fit, label="Average", color='black', linewidth=2)
    ax.set_title("Comparative Distribution Performance")
    ax.set_xlabel("Array Size (n)")
    ax.set_ylabel("Execution Time (seconds)")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_comparison(algo1_name, algo2_name, results, output_path):
    """Generates the 1x3 grid for comparing two algorithms."""
    sizes = results["sizes"]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Performance Comparison: {algo1_name.capitalize()} vs {algo2_name.capitalize()}", fontsize=15)

    for i, dist in enumerate(["random", "nearly_sorted", "reverse_sorted"]):
        ax = axes[i]
        t1 = results["algo1_times"][dist]
        t2 = results["algo2_times"][dist]
        
        ax.plot(sizes, t1, label=algo1_name.capitalize(), color="crimson", linewidth=2)
        ax.plot(sizes, t2, label=algo2_name.capitalize(), color="royalblue", linewidth=2, linestyle="--")
        
        ax.set_title(DIST_TITLES[dist])
        ax.set_xlabel("Array Size (n)")
        ax.set_ylabel("Execution Time (seconds)")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
