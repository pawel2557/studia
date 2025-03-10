import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]
        merge_sort(L)
        merge_sort(R)
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1


def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def measure_time(sort_function, arr):
    start_time = time.time()
    sort_function(arr)
    return time.time() - start_time


def run_experiment(repeats=5):
    sizes = [100, 500, 1000, 5000]
    results = []
    algorithms = {
        "Bubble Sort": bubble_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort
    }

    for size in sizes:
        for name, func in algorithms.items():
            times = []
            for _ in range(repeats):
                arr = random.sample(range(size * 10), size)
                arr_copy = arr.copy()
                if name == "Quick Sort":
                    exec_time = measure_time(lambda x: quick_sort(x), arr_copy)
                else:
                    exec_time = measure_time(func, arr_copy)
                times.append(exec_time)
            avg_time = sum(times) / len(times)
            results.append([size, name, avg_time])

    df = pd.DataFrame(results, columns=["Size", "Algorithm", "Avg Time (s)"])
    return df.pivot(index="Size", columns="Algorithm", values="Avg Time (s)")


df_results = run_experiment()


print("\n=== AVG SORT TIMES ===\n")
print(tabulate(df_results, headers='keys', tablefmt='fancy_grid', floatfmt=".6f"))

# Wykres
plt.figure(figsize=(10, 5))
for algo in df_results.columns:
    plt.plot(df_results.index, df_results[algo], marker='o', label=algo)
plt.xlabel("Size of Array")
plt.ylabel("Avg Time (seconds)")
plt.title("Sorting Algorithm Performance (Averaged)")
plt.legend()
plt.grid()
plt.show()
