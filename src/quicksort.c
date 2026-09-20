#include "quicksort.h"

// Créditos: Luis Henrique Sacchi
// Adaptado pelos autores.
static void swapInt(int arr[], int i1, int i2) {
    int temp = arr[i1];
    arr[i1] = arr[i2];
    arr[i2] = temp;
}

static int partition(int arr[], int low, int high) {
    int pivot = arr[high]; /// Escolhe o elemento piv�.
    int i = (low - 1);     /// Ajusta o �ndice dos elementos menores que o piv�.
    /// j vai at� o elemento anterior ao piv�.
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] <= pivot) {
            i++;
            swapInt(arr, i, j);
        }
    }
    swapInt(arr, (i + 1), high); /// Coloca o piv� na posi��o correta em termos de ordena��o
    return (i + 1);
}

static void quickSortRecursive(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);    /// pi � a posi��o do piv�, que j� � a correta
        quickSortRecursive(arr, low, pi - 1);  /// Ordena os elementos anteriores ao piv�
        quickSortRecursive(arr, pi + 1, high); /// Ordena os elementos posteriores ao piv�
    }
}

void quickSortAlgo(int arr[], int n) {
    if (!arr || n <= 1)
        return;

    quickSortRecursive(arr, 0, n - 1);
}
