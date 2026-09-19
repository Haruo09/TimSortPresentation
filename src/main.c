#include "timsort.h"
#include "utils.h"
#include <stdio.h>

int main() {
    int arr[] = {310, -2, 7, 15, -14, 0, 15, 0, 7, -7, -4, -13, 5, 8, -14, 12, 27, 305};
    // divide o peso total do array em bytes pelo peso de um único elemento para
    // descobrir o número de elementos do array
    int n = sizeof(arr) / sizeof(arr[0]);

    printf("Array original: ");
    printArray(arr, n);
    printf("\n");

    timSortAlgo(arr, n);
    printf("Depois de ordenar por Tim Sort: ");
    printArray(arr, n);

    return 0;
}
