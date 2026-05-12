# Java 03: Algorithms Part 1

Complete Java 17+ implementations of sorting, searching, greedy, divide-and-conquer, and backtracking algorithms.

---

## Table of Contents

### Section J: Sorting Algorithms
- [J.1 Bubble Sort](#j-1-bubble-sort)
- [J.2 Selection Sort](#j-2-selection-sort)
- [J.3 Insertion Sort](#j-3-insertion-sort)
- [J.4 Shell Sort](#j-4-shell-sort)
- [J.5 Merge Sort](#j-5-merge-sort)
- [J.6 Quick Sort](#j-6-quick-sort)
- [J.7 Heap Sort](#j-7-heap-sort)
- [J.8 Counting Sort](#j-8-counting-sort)
- [J.9 Radix Sort](#j-9-radix-sort)

### Section K: Searching Algorithms
- [K.1 Linear Search](#k-1-linear-search)
- [K.2 Binary Search](#k-2-binary-search)
- [K.3 Binary Search Variants](#k-3-binary-search-variants)

### Section L: Divide and Conquer
- [L.1 Closest Pair of Points](#l-1-closest-pair-of-points)
- [L.2 Kadane's Algorithm](#l-2-kadanes-algorithm)
- [L.3 Count Inversions](#l-3-count-inversions)

### Section M: Greedy Algorithms
- [M.1 Activity Selection](#m-1-activity-selection)
- [M.2 Fractional Knapsack](#m-2-fractional-knapsack)
- [M.3 Huffman Coding](#m-3-huffman-coding)

### Section N: Backtracking
- [N.1 N-Queens](#n-1-n-queens)
- [N.2 Sudoku Solver](#n-2-sudoku-solver)
- [N.3 Generate Subsets](#n-3-generate-subsets)

---

## Section J: Sorting Algorithms

---

### J.1 Bubble Sort

**Concept:** Repeatedly swap adjacent elements if out of order. Large elements "bubble" to end.

**Visual:**
```
Pass 1: [5, 3, 8, 1] -> [3, 5, 1, 8] (8 bubbles up)
Pass 2: [3, 5, 1, 8] -> [3, 1, 5, 8] (5 bubbles up)
Pass 3: [3, 1, 5, 8] -> [1, 3, 5, 8] (sorted)
```

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| Best | O(n) | O(1) | Yes |
| Average | O(n²) | O(1) | Yes |
| Worst | O(n²) | O(1) | Yes |

```java
/**
 * Bubble Sort - simplest sorting algorithm.
 * Educational purpose; rarely used in practice.
 */
public class BubbleSort {
    
    public static void sort(int[] arr) {
        var n = arr.length;
        
        for (var i = 0; i < n - 1; i++) {
            var swapped = false;
            
            // Last i elements are already in place
            for (var j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    // Swap
                    var temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            
            // Optimization: stop if no swaps
            if (!swapped) break;
        }
    }
}
```

**Key Points:**
- Simplest sort to understand and implement
- Adaptive - O(n) when nearly sorted
- Stable - maintains relative order of equal elements
- Only educational value; never use in production

---

### J.2 Selection Sort

**Concept:** Select minimum element and place at beginning. Unstable.

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| All | O(n²) | O(1) | No |

```java
/**
 * Selection Sort - repeatedly find minimum.
 */
public class SelectionSort {
    
    public static void sort(int[] arr) {
        var n = arr.length;
        
        for (var i = 0; i < n - 1; i++) {
            var minIdx = i;
            
            // Find minimum in unsorted portion
            for (var j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            
            // Swap with first unsorted position
            if (minIdx != i) {
                var temp = arr[i];
                arr[i] = arr[minIdx];
                arr[minIdx] = temp;
            }
        }
    }
}
```

---

### J.3 Insertion Sort

**Concept:** Build sorted array one element at a time by inserting into correct position.

**Visual:**
```
[5, 2, 4, 6, 1, 3]
[2, 5, 4, 6, 1, 3]  // Insert 2
[2, 4, 5, 6, 1, 3]  // Insert 4
[2, 4, 5, 6, 1, 3]  // Insert 6 (already in place)
[1, 2, 4, 5, 6, 3]  // Insert 1
[1, 2, 3, 4, 5, 6]  // Insert 3
```

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| Best | O(n) | O(1) | Yes |
| Average | O(n²) | O(1) | Yes |
| Worst | O(n²) | O(1) | Yes |

```java
/**
 * Insertion Sort - efficient for small or nearly sorted arrays.
 * Used as base case in TimSort and introsort.
 */
public class InsertionSort {
    
    public static void sort(int[] arr) {
        var n = arr.length;
        
        for (var i = 1; i < n; i++) {
            var key = arr[i];
            var j = i - 1;
            
            // Move elements greater than key one position right
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            
            arr[j + 1] = key;
        }
    }
    
    /**
     * Generic version for any Comparable type.
     */
    public static <T extends Comparable<T>> void sort(T[] arr) {
        var n = arr.length;
        
        for (var i = 1; i < n; i++) {
            var key = arr[i];
            var j = i - 1;
            
            while (j >= 0 && arr[j].compareTo(key) > 0) {
                arr[j + 1] = arr[j];
                j--;
            }
            
            arr[j + 1] = key;
        }
    }
}
```

**Key Points:**
- Best for small arrays (n < 50)
- Very efficient for nearly sorted data
- Used in Java's `Arrays.sort()` for small subarrays
- Stable and in-place

---

### J.4 Shell Sort

**Concept:** Generalized insertion sort with gap sequence.

**Complexity:**
| Case | Time | Space |
|------|:----:|:-----:|
| Best | O(n log n) | O(1) |
| Average | O(n^1.5) | O(1) |
| Worst | O(n²) | O(1) |

```java
/**
 * Shell Sort - insertion sort with gap reduction.
 */
public class ShellSort {
    
    public static void sort(int[] arr) {
        var n = arr.length;
        
        // Start with large gap, reduce by half
        for (var gap = n / 2; gap > 0; gap /= 2) {
            
            // Gapped insertion sort
            for (var i = gap; i < n; i++) {
                var temp = arr[i];
                var j = i;
                
                while (j >= gap && arr[j - gap] > temp) {
                    arr[j] = arr[j - gap];
                    j -= gap;
                }
                
                arr[j] = temp;
            }
        }
    }
}
```

---

### J.5 Merge Sort

**Concept:** Divide array in half, recursively sort, merge results.

**Visual:**
```
Divide:     [38, 27, 43, 3, 9, 82, 10]
           /                      \
     [38, 27, 43, 3]          [9, 82, 10]
       /          \              /        \
   [38, 27]   [43, 3]      [9, 82]    [10]
    /    \      /    \      /    \       |
 [38]  [27]  [43]   [3]  [9]   [82]  [10]

Merge:  [27, 38]    [3, 43]    [9, 82]   [10]
           \          /            \       /
        [3, 27, 38, 43]        [9, 10, 82]
                  \               /
         [3, 9, 10, 27, 38, 43, 82]
```

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| All | O(n log n) | O(n) | Yes |

```java
/**
 * Merge Sort - stable divide-and-conquer sort.
 * Guaranteed O(n log n), used in Java's Object sorting.
 */
public class MergeSort {
    
    public static void sort(int[] arr) {
        if (arr.length <= 1) return;
        
        var temp = new int[arr.length];
        sort(arr, temp, 0, arr.length - 1);
    }
    
    private static void sort(int[] arr, int[] temp, int left, int right) {
        if (left >= right) return;
        
        var mid = left + (right - left) / 2;
        
        // Divide
        sort(arr, temp, left, mid);
        sort(arr, temp, mid + 1, right);
        
        // Conquer (merge)
        merge(arr, temp, left, mid, right);
    }
    
    private static void merge(int[] arr, int[] temp, int left, int mid, int right) {
        // Copy to temp
        for (var i = left; i <= right; i++) {
            temp[i] = arr[i];
        }
        
        var i = left;      // Left subarray
        var j = mid + 1;   // Right subarray
        var k = left;      // Merged array
        
        // Merge smaller elements first
        while (i <= mid && j <= right) {
            if (temp[i] <= temp[j]) {
                arr[k++] = temp[i++];
            } else {
                arr[k++] = temp[j++];
            }
        }
        
        // Copy remaining elements
        while (i <= mid) arr[k++] = temp[i++];
        while (j <= right) arr[k++] = temp[j++];
    }
    
    /**
     * Bottom-up iterative version (no recursion).
     */
    public static void sortBottomUp(int[] arr) {
        var n = arr.length;
        var temp = new int[n];
        
        for (var size = 1; size < n; size *= 2) {
            for (var left = 0; left < n - size; left += 2 * size) {
                var mid = left + size - 1;
                var right = Math.min(left + 2 * size - 1, n - 1);
                merge(arr, temp, left, mid, right);
            }
        }
    }
}
```

**Key Points:**
- Stable and guaranteed O(n log n)
- Used in Java's `Arrays.sort(Object[])`
- External sorting variant for large datasets
- Merge step can be parallelized

---

### J.6 Quick Sort

**Concept:** Pick pivot, partition around it, recursively sort partitions.

**Visual (Lomuto partition):**
```
[10, 80, 30, 90, 40, 50, 70]  pivot = 70

Partition:
[10, 30, 40, 50]  [70]  [80, 90]

Recursively sort left and right
```

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| Best | O(n log n) | O(log n) | No |
| Average | O(n log n) | O(log n) | No |
| Worst | O(n²) | O(n) | No |

```java
/**
 * Quick Sort - fastest in practice for primitive types.
 * Used in Java's Arrays.sort(int[]) via Dual-Pivot Quicksort.
 */
public class QuickSort {
    
    public static void sort(int[] arr) {
        sort(arr, 0, arr.length - 1);
    }
    
    private static void sort(int[] arr, int low, int high) {
        if (low < high) {
            // Use insertion sort for small subarrays
            if (high - low + 1 <= 10) {
                insertionSort(arr, low, high);
                return;
            }
            
            var pivot = partition(arr, low, high);
            sort(arr, low, pivot - 1);
            sort(arr, pivot + 1, high);
        }
    }
    
    /**
     * Hoare partition scheme (more efficient than Lomuto).
     */
    private static int partition(int[] arr, int low, int high) {
        // Median-of-three pivot selection
        var mid = low + (high - low) / 2;
        medianOfThree(arr, low, mid, high);
        
        var pivot = arr[low];
        var i = low - 1;
        var j = high + 1;
        
        while (true) {
            do { i++; } while (arr[i] < pivot);
            do { j--; } while (arr[j] > pivot);
            
            if (i >= j) return j;
            
            swap(arr, i, j);
        }
    }
    
    /**
     * Lomuto partition (simpler, less efficient).
     */
    private static int partitionLomuto(int[] arr, int low, int high) {
        var pivot = arr[high];
        var i = low - 1;
        
        for (var j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        
        swap(arr, i + 1, high);
        return i + 1;
    }
    
    /**
     * 3-way partition for arrays with duplicates (Dutch National Flag).
     */
    public static void sort3Way(int[] arr) {
        sort3Way(arr, 0, arr.length - 1);
    }
    
    private static void sort3Way(int[] arr, int low, int high) {
        if (high <= low) return;
        
        var lt = low;
        var gt = high;
        var pivot = arr[low];
        var i = low;
        
        while (i <= gt) {
            var cmp = Integer.compare(arr[i], pivot);
            
            switch (cmp) {
                case -1 -> swap(arr, lt++, i++);
                case 0 -> i++;
                case 1 -> swap(arr, i, gt--);
            }
        }
        
        sort3Way(arr, low, lt - 1);
        sort3Way(arr, gt + 1, high);
    }
    
    private static void medianOfThree(int[] arr, int a, int b, int c) {
        if (arr[a] > arr[b]) swap(arr, a, b);
        if (arr[a] > arr[c]) swap(arr, a, c);
        if (arr[b] > arr[c]) swap(arr, b, c);
    }
    
    private static void swap(int[] arr, int i, int j) {
        var temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    private static void insertionSort(int[] arr, int low, int high) {
        for (var i = low + 1; i <= high; i++) {
            var key = arr[i];
            var j = i - 1;
            
            while (j >= low && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            
            arr[j + 1] = key;
        }
    }
}
```

**Key Points:**
- Fastest in practice for primitive types
- Hoare partition more efficient than Lomuto
- 3-way partition handles duplicates efficiently
- Median-of-three avoids worst case
- Used in Java's `Arrays.sort(int[])`

---

### J.7 Heap Sort

**Concept:** Build max heap, repeatedly extract maximum.

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| All | O(n log n) | O(1) | No |

```java
/**
 * Heap Sort - in-place O(n log n) sort.
 * Guaranteed worst case, no extra space needed.
 */
public class HeapSort {
    
    public static void sort(int[] arr) {
        var n = arr.length;
        
        // Build max heap (bottom-up)
        for (var i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }
        
        // Extract elements one by one
        for (var i = n - 1; i > 0; i--) {
            // Move current root to end
            swap(arr, 0, i);
            
            // Heapify reduced heap
            heapify(arr, i, 0);
        }
    }
    
    private static void heapify(int[] arr, int n, int i) {
        var largest = i;
        var left = 2 * i + 1;
        var right = 2 * i + 2;
        
        if (left < n && arr[left] > arr[largest]) {
            largest = left;
        }
        
        if (right < n && arr[right] > arr[largest]) {
            largest = right;
        }
        
        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, n, largest);
        }
    }
    
    private static void swap(int[] arr, int i, int j) {
        var temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

**Key Points:**
- In-place O(n log n) with O(1) extra space
- Guaranteed worst case (unlike QuickSort)
- Not stable
- Used when memory is constrained

---

### J.8 Counting Sort

**Concept:** Count occurrences, compute prefix sums, place elements.

**Complexity:**
| Case | Time | Space | Stable |
|------|:----:|:-----:|:------:|
| All | O(n + k) | O(k) | Yes |

```java
/**
 * Counting Sort - O(n) for integer keys in known range.
 * Non-comparison sort, stable.
 */
public class CountingSort {
    
    public static void sort(int[] arr) {
        if (arr.length <= 1) return;
        
        // Find range
        var min = arr[0];
        var max = arr[0];
        for (var num : arr) {
            if (num < min) min = num;
            if (num > max) max = num;
        }
        
        var range = max - min + 1;
        var count = new int[range];
        
        // Count occurrences
        for (var num : arr) {
            count[num - min]++;
        }
        
        // Compute prefix sums (cumulative count)
        for (var i = 1; i < range; i++) {
            count[i] += count[i - 1];
        }
        
        // Place elements in output (stable)
        var output = new int[arr.length];
        for (var i = arr.length - 1; i >= 0; i--) {
            var idx = count[arr[i] - min] - 1;
            output[idx] = arr[i];
            count[arr[i] - min]--;
        }
        
        // Copy back
        System.arraycopy(output, 0, arr, 0, arr.length);
    }
}
```

**Key Points:**
- O(n) when k (range) is O(n)
- Stable and preserves order
- Used as subroutine in Radix Sort
- Only works with integer keys in known range

---

### J.9 Radix Sort

**Concept:** Sort by digits from LSD to MSD using counting sort.

**Complexity:**
| Case | Time | Space |
|------|:----:|:-----:|
| All | O(d × (n + k)) | O(n + k) |

```java
/**
 * Radix Sort - sorts integers digit by digit.
 * Stable, linear time for fixed digit length.
 */
public class RadixSort {
    
    public static void sort(int[] arr) {
        if (arr.length <= 1) return;
        
        // Find maximum to determine number of digits
        var max = arr[0];
        for (var num : arr) {
            if (num > max) max = num;
        }
        
        // Do counting sort for every digit
        for (var exp = 1; max / exp > 0; exp *= 10) {
            countingSortByDigit(arr, exp);
        }
    }
    
    private static void countingSortByDigit(int[] arr, int exp) {
        var n = arr.length;
        var output = new int[n];
        var count = new int[10]; // Digits 0-9
        
        // Count occurrences of digit
        for (var num : arr) {
            var digit = (num / exp) % 10;
            count[digit]++;
        }
        
        // Prefix sum
        for (var i = 1; i < 10; i++) {
            count[i] += count[i - 1];
        }
        
        // Build output (stable - process from end)
        for (var i = n - 1; i >= 0; i--) {
            var digit = (arr[i] / exp) % 10;
            output[count[digit] - 1] = arr[i];
            count[digit]--;
        }
        
        System.arraycopy(output, 0, arr, 0, n);
    }
    
    /**
     * Handle negative numbers using offset.
     */
    public static void sortWithNegatives(int[] arr) {
        // Find range
        var min = Integer.MAX_VALUE;
        var max = Integer.MIN_VALUE;
        for (var num : arr) {
            if (num < min) min = num;
            if (num > max) max = num;
        }
        
        // Offset to make all non-negative
        var offset = -min;
        var offsetArr = new int[arr.length];
        for (var i = 0; i < arr.length; i++) {
            offsetArr[i] = arr[i] + offset;
        }
        
        sort(offsetArr);
        
        // Restore
        for (var i = 0; i < arr.length; i++) {
            arr[i] = offsetArr[i] - offset;
        }
    }
}
```

**Key Points:**
- Linear time for fixed-length integers
- Used in sorting large integers, strings
- Stable when using stable counting sort
- LSD (least significant digit) first

---

## Section K: Searching Algorithms

---

### K.2 Binary Search

**Concept:** Divide search interval in half repeatedly.

**Visual:**
```
[1, 3, 5, 7, 9, 11, 13]  target = 7
     ^
   mid = 7 (found!)

If target = 10:
[1, 3, 5, 7, 9, 11, 13]
         ^
       mid = 7, go right
[9, 11, 13]
   ^
 mid = 11, go left
[9]
 ^
not found
```

**Complexity:**
| Case | Time | Space |
|------|:----:|:-----:|
| All | O(log n) | O(1) |

```java
/**
 * Binary Search - O(log n) search in sorted array.
 * Foundation for many advanced algorithms.
 */
public class BinarySearch {
    
    /**
     * Iterative binary search.
     */
    public static int search(int[] arr, int target) {
        var left = 0;
        var right = arr.length - 1;
        
        while (left <= right) {
            var mid = left + (right - left) / 2;
            
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1; // Not found
    }
    
    /**
     * Recursive binary search.
     */
    public static int searchRecursive(int[] arr, int target) {
        return searchRecursive(arr, target, 0, arr.length - 1);
    }
    
    private static int searchRecursive(int[] arr, int target, int left, int right) {
        if (left > right) return -1;
        
        var mid = left + (right - left) / 2;
        
        return switch (Integer.compare(arr[mid], target)) {
            case 0 -> mid;
            case -1 -> searchRecursive(arr, target, mid + 1, right);
            case 1 -> searchRecursive(arr, target, left, mid - 1);
            default -> -1;
        };
    }
    
    /**
     * Lower bound: first index where arr[i] >= target.
     */
    public static int lowerBound(int[] arr, int target) {
        var left = 0;
        var right = arr.length;
        
        while (left < right) {
            var mid = left + (right - left) / 2;
            if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        
        return left;
    }
    
    /**
     * Upper bound: first index where arr[i] > target.
     */
    public static int upperBound(int[] arr, int target) {
        var left = 0;
        var right = arr.length;
        
        while (left < right) {
            var mid = left + (right - left) / 2;
            if (arr[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        
        return left;
    }
    
    /**
     * Find first occurrence of target.
     */
    public static int firstOccurrence(int[] arr, int target) {
        var idx = lowerBound(arr, target);
        return (idx < arr.length && arr[idx] == target) ? idx : -1;
    }
    
    /**
     * Find last occurrence of target.
     */
    public static int lastOccurrence(int[] arr, int target) {
        var idx = upperBound(arr, target) - 1;
        return (idx >= 0 && arr[idx] == target) ? idx : -1;
    }
    
    /**
     * Search in rotated sorted array (e.g., [4,5,6,7,0,1,2]).
     */
    public static int searchRotated(int[] arr, int target) {
        var left = 0;
        var right = arr.length - 1;
        
        while (left <= right) {
            var mid = left + (right - left) / 2;
            
            if (arr[mid] == target) return mid;
            
            // Check which half is sorted
            if (arr[left] <= arr[mid]) {
                // Left half is sorted
                if (target >= arr[left] && target < arr[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                // Right half is sorted
                if (target > arr[mid] && target <= arr[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        
        return -1;
    }
}
```

**Key Points:**
- Template for many "search in sorted" problems
- `left + (right - left) / 2` prevents overflow
- Lower/upper bounds essential for range queries
- Rotated array search tests understanding

---

## Section L: Divide and Conquer

---

### L.2 Kadane's Algorithm

**Concept:** Find maximum subarray sum in linear time.

**Complexity:**
| Case | Time | Space |
|------|:----:|:-----:|
| All | O(n) | O(1) |

```java
/**
 * Kadane's Algorithm - maximum subarray sum.
 * Can be extended to track subarray indices.
 */
public class KadaneAlgorithm {
    
    /**
     * Basic version - returns max sum only.
     */
    public static int maxSubArraySum(int[] arr) {
        if (arr.length == 0) return 0;
        
        var maxSoFar = arr[0];
        var maxEndingHere = arr[0];
        
        for (var i = 1; i < arr.length; i++) {
            // Either extend previous subarray or start new
            maxEndingHere = Math.max(arr[i], maxEndingHere + arr[i]);
            maxSoFar = Math.max(maxSoFar, maxEndingHere);
        }
        
        return maxSoFar;
    }
    
    /**
     * Extended version - returns [maxSum, start, end].
     */
    public static int[] maxSubArrayWithIndices(int[] arr) {
        if (arr.length == 0) return new int[] {0, -1, -1};
        
        var maxSoFar = arr[0];
        var maxEndingHere = arr[0];
        var start = 0, end = 0;
        var tempStart = 0;
        
        for (var i = 1; i < arr.length; i++) {
            if (maxEndingHere + arr[i] < arr[i]) {
                maxEndingHere = arr[i];
                tempStart = i;
            } else {
                maxEndingHere += arr[i];
            }
            
            if (maxEndingHere > maxSoFar) {
                maxSoFar = maxEndingHere;
                start = tempStart;
                end = i;
            }
        }
        
        return new int[] {maxSoFar, start, end};
    }
    
    /**
     * Circular array version (max subarray sum with wrap-around).
     */
    public static int maxCircularSubArraySum(int[] arr) {
        var maxKadane = maxSubArraySum(arr);
        
        // Handle all negative case
        if (maxKadane < 0) return maxKadane;
        
        // Total sum - min subarray sum = max circular subarray
        var totalSum = 0;
        for (var num : arr) totalSum += num;
        
        // Invert array and find min subarray
        var inverted = new int[arr.length];
        for (var i = 0; i < arr.length; i++) {
            inverted[i] = -arr[i];
        }
        var minSubarraySum = -maxSubArraySum(inverted);
        
        return Math.max(maxKadane, totalSum - minSubarraySum);
    }
}
```

**Key Points:**
- Classic DP example with O(1) space
- Greedy choice: extend or start fresh
- Variations: 2D, circular, with constraints

---

*Continue with other sections...*

## Section M: Greedy Algorithms

---

### M.1 Activity Selection

**Concept:** Select maximum non-overlapping activities.

```java
/**
 * Activity Selection - classic greedy problem.
 * Sort by finish time, pick compatible activities.
 */
public class ActivitySelection {
    
    private record Activity(int start, int end, String name) 
        implements Comparable<Activity> {
        
        @Override
        public int compareTo(Activity other) {
            return Integer.compare(this.end, other.end);
        }
    }
    
    public static List<Activity> selectActivities(List<Activity> activities) {
        if (activities.isEmpty()) return Collections.emptyList();
        
        // Sort by finish time
        var sorted = new ArrayList<>(activities);
        Collections.sort(sorted);
        
        var result = new ArrayList<Activity>();
        var lastEnd = -1;
        
        for (var activity : sorted) {
            if (activity.start >= lastEnd) {
                result.add(activity);
                lastEnd = activity.end;
            }
        }
        
        return result;
    }
}
```

---

### M.2 Fractional Knapsack

**Concept:** Take items with best value-to-weight ratio.

```java
/**
 * Fractional Knapsack - greedy works here (unlike 0/1 knapsack).
 */
public class FractionalKnapsack {
    
    private record Item(double weight, double value, String name) {
        double ratio() {
            return value / weight;
        }
    }
    
    public static double getMaxValue(Item[] items, double capacity) {
        // Sort by value-to-weight ratio descending
        Arrays.sort(items, (a, b) -> 
            Double.compare(b.ratio(), a.ratio()));
        
        var totalValue = 0.0;
        var remaining = capacity;
        
        for (var item : items) {
            if (remaining >= item.weight) {
                // Take whole item
                totalValue += item.value;
                remaining -= item.weight;
            } else {
                // Take fraction
                totalValue += item.ratio() * remaining;
                break;
            }
        }
        
        return totalValue;
    }
}
```

---

## Section N: Backtracking

---

### N.1 N-Queens

**Concept:** Place N queens on N×N board without attacking each other.

```java
/**
 * N-Queens - classic backtracking problem.
 * Uses sets for O(1) conflict checking.
 */
public class NQueens {
    
    private List<List<String>> solutions;
    private int n;
    
    public List<List<String>> solveNQueens(int n) {
        this.n = n;
        this.solutions = new ArrayList<>();
        
        // Sets for O(1) conflict detection
        var cols = new HashSet<Integer>();
        var diagonals = new HashSet<Integer>();     // row - col
        var antiDiagonals = new HashSet<Integer>(); // row + col
        
        var board = new char[n][n];
        for (var row : board) {
            Arrays.fill(row, '.');
        }
        
        backtrack(0, board, cols, diagonals, antiDiagonals);
        
        return solutions;
    }
    
    private void backtrack(int row, char[][] board,
                          Set<Integer> cols,
                          Set<Integer> diagonals,
                          Set<Integer> antiDiagonals) {
        
        if (row == n) {
            solutions.add(constructBoard(board));
            return;
        }
        
        for (var col = 0; col < n; col++) {
            var diag = row - col;
            var antiDiag = row + col;
            
            // Check if position is under attack
            if (cols.contains(col) || 
                diagonals.contains(diag) || 
                antiDiagonals.contains(antiDiag)) {
                continue;
            }
            
            // Place queen
            board[row][col] = 'Q';
            cols.add(col);
            diagonals.add(diag);
            antiDiagonals.add(antiDiag);
            
            // Recurse
            backtrack(row + 1, board, cols, diagonals, antiDiagonals);
            
            // Backtrack
            board[row][col] = '.';
            cols.remove(col);
            diagonals.remove(diag);
            antiDiagonals.remove(antiDiag);
        }
    }
    
    private List<String> constructBoard(char[][] board) {
        var result = new ArrayList<String>();
        for (var row : board) {
            result.add(new String(row));
        }
        return result;
    }
    
    /**
     * Count solutions without storing them.
     */
    public int countNQueens(int n) {
        // Same logic, just count instead of store
        return countSolutions(0, new HashSet<>(), 
                             new HashSet<>(), 
                             new HashSet<>());
    }
    
    private int countSolutions(int row, Set<Integer> cols,
                               Set<Integer> diags, 
                               Set<Integer> antiDiags) {
        if (row == n) return 1;
        
        var count = 0;
        for (var col = 0; col < n; col++) {
            if (!cols.contains(col) && 
                !diags.contains(row - col) && 
                !antiDiags.contains(row + col)) {
                
                cols.add(col);
                diags.add(row - col);
                antiDiags.add(row + col);
                
                count += countSolutions(row + 1, cols, diags, antiDiags);
                
                cols.remove(col);
                diags.remove(row - col);
                antiDiags.remove(row + col);
            }
        }
        return count;
    }
}
```

**Key Points:**
- Sets for O(1) conflict checking
- Backtracking explores all valid configurations
- Pruning via early conflict detection
- Bitmask optimization possible

---

*Continue with more algorithms...*