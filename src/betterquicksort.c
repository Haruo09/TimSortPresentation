#include "quicksort.h"
#include <stddef.h>

#define CUTOFF 16

static void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

static void insertionSortRange(int *arr, int low, int high) {
    for (int i = low + 1; i <= high; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= low && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// Median-of-Three pivot selection
static int medianOfThree(int *arr, int low, int high) {
    int mid = low + (high - low) / 2;

    if (arr[low] > arr[mid])
        swap(&arr[low], &arr[mid]);
    if (arr[low] > arr[high])
        swap(&arr[low], &arr[high]);
    if (arr[mid] > arr[high])
        swap(&arr[mid], &arr[high]);

    // Place pivot at high - 1 position
    swap(&arr[mid], &arr[high - 1]);
    return arr[high - 1];
}

static int partition(int *arr, int low, int high) {
    int pivot = medianOfThree(arr, low, high);
    int i = low;
    int j = high - 1;

    while (1) {
        while (arr[++i] < pivot)
            ;
        while (arr[--j] > pivot)
            ;

        if (i >= j)
            break;

        swap(&arr[i], &arr[j]);
    }

    swap(&arr[i], &arr[high - 1]);
    return i;
}

static void quickSortRecursive(int *arr, int low, int high) {
    while (high - low >= CUTOFF) {
        int pivotIndex = partition(arr, low, high);

        // Recurse on smaller partition first to optimize call stack space
        if (pivotIndex - low < high - pivotIndex) {
            quickSortRecursive(arr, low, pivotIndex - 1);
            low = pivotIndex + 1;
        } else {
            quickSortRecursive(arr, pivotIndex + 1, high);
            high = pivotIndex - 1;
        }
    }
    // Final pass on small subarray using Insertion Sort
    insertionSortRange(arr, low, high);
}

void betterQuickSortAlgo(int *arr, int n) {
    if (!arr || n <= 1)
        return;
    quickSortRecursive(arr, 0, n - 1);
}
