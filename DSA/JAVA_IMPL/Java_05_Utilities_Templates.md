# Java 05: Utilities and Templates

Helper classes, common patterns, comparator utilities, and testing templates for Java DSA implementations.

---

## Table of Contents

- [Common Data Classes](#common-data-classes)
- [Comparator Utilities](#comparator-utilities)
- [Math Utilities](#math-utilities)
- [Array Utilities](#array-utilities)
- [Testing Templates](#testing-templates)

---

## Common Data Classes

### Generic Pair and Tuple

```java
/**
 * Generic Pair class for storing key-value pairs.
 * Used throughout DSA implementations.
 */
public record Pair<K, V>(K key, V value) {
    
    public static <K, V> Pair<K, V> of(K key, V value) {
        return new Pair<>(key, value);
    }
    
    @Override
    public String toString() {
        return "(" + key + ", " + value + ")";
    }
}

/**
 * IntPair for primitive int pairs (more memory efficient).
 */
public record IntPair(int first, int second) {
    
    public static IntPair of(int first, int second) {
        return new IntPair(first, second);
    }
    
    public int sum() { return first + second; }
    public int diff() { return first - second; }
    public long product() { return (long) first * second; }
}

/**
 * Triple for three values.
 */
public record Triple<A, B, C>(A first, B second, C third) {
    
    public static <A, B, C> Triple<A, B, C> of(A first, B second, C third) {
        return new Triple<>(first, second, third);
    }
}
```

### Graph Edge Classes

```java
/**
 * Edge for weighted graphs.
 */
public record WeightedEdge(int from, int to, int weight) 
    implements Comparable<WeightedEdge> {
    
    @Override
    public int compareTo(WeightedEdge other) {
        return Integer.compare(this.weight, other.weight);
    }
    
    public WeightedEdge reversed() {
        return new WeightedEdge(to, from, weight);
    }
}

/**
 * Edge for unweighted graphs.
 */
public record Edge(int from, int to) {
    
    public Edge reversed() {
        return new Edge(to, from);
    }
}

/**
 * Directed edge with additional information.
 */
public record DirectedEdge(int from, int to, int weight, String label) {
    
    public boolean isSelfLoop() {
        return from == to;
    }
}
```

### Tree Node Classes

```java
/**
 * Binary Tree Node with parent reference.
 */
public class TreeNode<T> {
    T data;
    TreeNode<T> left;
    TreeNode<T> right;
    TreeNode<T> parent;
    
    public TreeNode(T data) {
        this.data = data;
    }
    
    public boolean isLeaf() {
        return left == null && right == null;
    }
    
    public int height() {
        var leftHeight = (left == null) ? 0 : left.height();
        var rightHeight = (right == null) ? 0 : right.height();
        return 1 + Math.max(leftHeight, rightHeight);
    }
}

/**
 * N-ary Tree Node.
 */
public class NaryTreeNode<T> {
    T data;
    List<NaryTreeNode<T>> children;
    
    public NaryTreeNode(T data) {
        this.data = data;
        this.children = new ArrayList<>();
    }
}
```

---

## Comparator Utilities

```java
/**
 * Utility class for creating comparators.
 */
public class Comparators {
    
    /**
     * Compare by multiple fields (lexicographic ordering).
     */
    @SafeVarargs
    public static <T> Comparator<T> compareBy(Comparator<? super T>... comparators) {
        return (a, b) -> {
            for (var comp : comparators) {
                var result = comp.compare(a, b);
                if (result != 0) return result;
            }
            return 0;
        };
    }
    
    /**
     * Reverse comparator (descending order).
     */
    public static <T> Comparator<T> reverse(Comparator<T> comparator) {
        return comparator.reversed();
    }
    
    /**
     * Nulls first comparator.
     */
    public static <T> Comparator<T> nullsFirst(Comparator<? super T> comparator) {
        return Comparator.nullsFirst(comparator);
    }
    
    /**
     * Comparator for sorting by length of string.
     */
    public static Comparator<String> byLength() {
        return Comparator.comparingInt(String::length);
    }
    
    /**
     * Comparator for sorting by absolute value.
     */
    public static Comparator<Integer> byAbsoluteValue() {
        return Comparator.comparingInt(Math::abs);
    }
    
    /**
     * Priority for custom objects.
     */
    public interface Priority<T> {
        int getPriority(T item);
    }
}
```

---

## Math Utilities

```java
/**
 * Mathematical utilities for DSA.
 */
public class MathUtils {
    
    static final int MOD = 1_000_000_007;
    
    /**
     * Fast exponentiation (binary exponentiation).
     * Time: O(log n)
     */
    public static long fastPow(long base, long exp) {
        return fastPow(base, exp, MOD);
    }
    
    public static long fastPow(long base, long exp, long mod) {
        var result = 1L;
        base %= mod;
        
        while (exp > 0) {
            if ((exp & 1) == 1) {
                result = (result * base) % mod;
            }
            base = (base * base) % mod;
            exp >>= 1;
        }
        
        return result;
    }
    
    /**
     * Modular multiplicative inverse using Fermat's little theorem.
     * Works when mod is prime.
     */
    public static long modInverse(long a, long mod) {
        return fastPow(a, mod - 2, mod);
    }
    
    /**
     * GCD using Euclidean algorithm.
     * Time: O(log min(a, b))
     */
    public static int gcd(int a, int b) {
        while (b != 0) {
            var temp = b;
            b = a % b;
            a = temp;
        }
        return Math.abs(a);
    }
    
    public static long gcd(long a, long b) {
        while (b != 0) {
            var temp = b;
            b = a % b;
            a = temp;
        }
        return Math.abs(a);
    }
    
    /**
     * LCM using GCD.
     */
    public static long lcm(long a, long b) {
        return Math.abs(a / gcd(a, b) * b);
    }
    
    /**
     * Extended Euclidean algorithm.
     * Returns [gcd, x, y] where ax + by = gcd(a, b)
     */
    public static long[] extendedGcd(long a, long b) {
        if (b == 0) {
            return new long[] {a, 1, 0};
        }
        
        var vals = extendedGcd(b, a % b);
        var g = vals[0];
        var x1 = vals[1];
        var y1 = vals[2];
        
        var x = y1;
        var y = x1 - (a / b) * y1;
        
        return new long[] {g, x, y};
    }
    
    /**
     * Check if number is prime (trial division).
     * Time: O(√n)
     */
    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        if (n <= 3) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        
        for (var i = 5; i * i <= n; i += 6) {
            if (n % i == 0 || n % (i + 2) == 0) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Sieve of Eratosthenes.
     * Time: O(n log log n), Space: O(n)
     */
    public static boolean[] sieve(int n) {
        var isPrime = new boolean[n + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        
        for (var i = 2; i * i <= n; i++) {
            if (isPrime[i]) {
                for (var j = i * i; j <= n; j += i) {
                    isPrime[j] = false;
                }
            }
        }
        
        return isPrime;
    }
    
    /**
     * Factorial with modulo.
     */
    public static long factorial(int n) {
        var result = 1L;
        for (var i = 2; i <= n; i++) {
            result = (result * i) % MOD;
        }
        return result;
    }
    
    /**
     * Combination nCr with modulo.
     */
    public static long nCr(int n, int r) {
        if (r > n || r < 0) return 0;
        
        var numerator = 1L;
        var denominator = 1L;
        
        r = Math.min(r, n - r);
        
        for (var i = 0; i < r; i++) {
            numerator = (numerator * (n - i)) % MOD;
            denominator = (denominator * (i + 1)) % MOD;
        }
        
        return (numerator * modInverse(denominator, MOD)) % MOD;
    }
    
    /**
     * Catalan number C_n = (2n choose n) / (n + 1)
     */
    public static long catalan(int n) {
        return (nCr(2 * n, n) * modInverse(n + 1, MOD)) % MOD;
    }
}
```

---

## Array Utilities

```java
/**
 * Utility methods for array manipulation.
 */
public class ArrayUtils {
    
    /**
     * Swap two elements in array.
     */
    public static void swap(int[] arr, int i, int j) {
        var temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    public static void swap(Object[] arr, int i, int j) {
        var temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    /**
     * Reverse array in-place.
     */
    public static void reverse(int[] arr) {
        reverse(arr, 0, arr.length - 1);
    }
    
    public static void reverse(int[] arr, int left, int right) {
        while (left < right) {
            swap(arr, left++, right--);
        }
    }
    
    /**
     * Rotate array right by k positions.
     */
    public static void rotate(int[] arr, int k) {
        var n = arr.length;
        k %= n;
        if (k < 0) k += n;
        
        reverse(arr, 0, n - 1);
        reverse(arr, 0, k - 1);
        reverse(arr, k, n - 1);
    }
    
    /**
     * Find maximum element.
     */
    public static int max(int[] arr) {
        return Arrays.stream(arr).max().orElse(Integer.MIN_VALUE);
    }
    
    /**
     * Find minimum element.
     */
    public static int min(int[] arr) {
        return Arrays.stream(arr).min().orElse(Integer.MAX_VALUE);
    }
    
    /**
     * Calculate sum.
     */
    public static long sum(int[] arr) {
        return Arrays.stream(arr).asLongStream().sum();
    }
    
    /**
     * Prefix sum array.
     */
    public static int[] prefixSum(int[] arr) {
        var n = arr.length;
        var prefix = new int[n + 1];
        
        for (var i = 0; i < n; i++) {
            prefix[i + 1] = prefix[i] + arr[i];
        }
        
        return prefix;
    }
    
    /**
     * Range sum using prefix array.
     */
    public static int rangeSum(int[] prefix, int left, int right) {
        return prefix[right + 1] - prefix[left];
    }
    
    /**
     * Frequency map of array elements.
     */
    public static Map<Integer, Integer> frequencyMap(int[] arr) {
        var map = new HashMap<Integer, Integer>();
        for (var num : arr) {
            map.merge(num, 1, Integer::sum);
        }
        return map;
    }
    
    /**
     * Find majority element (appears more than n/2 times).
     * Boyer-Moore Voting Algorithm.
     */
    public static Integer majorityElement(int[] arr) {
        var candidate = 0;
        var count = 0;
        
        for (var num : arr) {
            if (count == 0) {
                candidate = num;
                count = 1;
            } else if (num == candidate) {
                count++;
            } else {
                count--;
            }
        }
        
        // Verify
        var finalCandidate = candidate;
        var freq = Arrays.stream(arr).filter(x -> x == finalCandidate).count();
        
        return freq > arr.length / 2 ? candidate : null;
    }
    
    /**
     * Next permutation (lexicographically next greater permutation).
     */
    public static boolean nextPermutation(int[] arr) {
        var n = arr.length;
        
        // Find first decreasing element from right
        var i = n - 2;
        while (i >= 0 && arr[i] >= arr[i + 1]) {
            i--;
        }
        
        if (i >= 0) {
            // Find element just larger than arr[i]
            var j = n - 1;
            while (j >= 0 && arr[j] <= arr[i]) {
                j--;
            }
            swap(arr, i, j);
        }
        
        reverse(arr, i + 1, n - 1);
        return i >= 0;
    }
    
    /**
     * Generate all permutations.
     */
    public static List<List<Integer>> permutations(int[] arr) {
        var result = new ArrayList<List<Integer>>();
        backtrack(arr, 0, result);
        return result;
    }
    
    private static void backtrack(int[] arr, int start, List<List<Integer>> result) {
        if (start == arr.length) {
            var list = new ArrayList<Integer>();
            for (var num : arr) list.add(num);
            result.add(list);
            return;
        }
        
        for (var i = start; i < arr.length; i++) {
            swap(arr, start, i);
            backtrack(arr, start + 1, result);
            swap(arr, start, i);
        }
    }
}
```

---

## Testing Templates

```java
/**
 * Simple testing framework for DSA implementations.
 */
public class TestUtils {
    
    private static int testsPassed = 0;
    private static int testsFailed = 0;
    
    /**
     * Assert equals for primitives.
     */
    public static void assertEquals(int expected, int actual, String message) {
        if (expected != actual) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + expected);
            System.err.println("  Actual: " + actual);
            testsFailed++;
        } else {
            testsPassed++;
        }
    }
    
    public static void assertEquals(long expected, long actual, String message) {
        if (expected != actual) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + expected);
            System.err.println("  Actual: " + actual);
            testsFailed++;
        } else {
            testsPassed++;
        }
    }
    
    public static void assertEquals(boolean expected, boolean actual, String message) {
        if (expected != actual) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + expected);
            System.err.println("  Actual: " + actual);
            testsFailed++;
        } else {
            testsPassed++;
        }
    }
    
    public static void assertArrayEquals(int[] expected, int[] actual, String message) {
        if (!Arrays.equals(expected, actual)) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + Arrays.toString(expected));
            System.err.println("  Actual: " + Arrays.toString(actual));
            testsFailed++;
        } else {
            testsPassed++;
        }
    }
    
    /**
     * Assert true.
     */
    public static void assertTrue(boolean condition, String message) {
        if (!condition) {
            System.err.println("FAIL: " + message);
            testsFailed++;
        } else {
            testsPassed++;
        }
    }
    
    /**
     * Print test results summary.
     */
    public static void printResults() {
        System.out.println("\n=== Test Results ===");
        System.out.println("Passed: " + testsPassed);
        System.out.println("Failed: " + testsFailed);
        System.out.println("Total:  " + (testsPassed + testsFailed));
        
        if (testsFailed == 0) {
            System.out.println("All tests passed! ✓");
        } else {
            System.out.println("Some tests failed! ✗");
            System.exit(1);
        }
    }
    
    /**
     * Reset counters.
     */
    public static void reset() {
        testsPassed = 0;
        testsFailed = 0;
    }
    
    /**
     * Time an operation.
     */
    public static long timeOperation(Runnable operation) {
        var start = System.nanoTime();
        operation.run();
        var end = System.nanoTime();
        return (end - start) / 1_000_000; // Convert to milliseconds
    }
    
    /**
     * Print execution time.
     */
    public static void printTime(String operation, Runnable runnable) {
        var time = timeOperation(runnable);
        System.out.println(operation + ": " + time + " ms");
    }
}

/**
 * Example test usage.
 */
class ExampleTests {
    public static void main(String[] args) {
        // Test sorting
        var arr = new int[] {5, 2, 8, 1, 9};
        Arrays.sort(arr);
        TestUtils.assertArrayEquals(new int[] {1, 2, 5, 8, 9}, arr, "Sorting test");
        
        // Test math
        TestUtils.assertEquals(6, MathUtils.gcd(12, 18), "GCD test");
        TestUtils.assertEquals(36, MathUtils.lcm(12, 18), "LCM test");
        TestUtils.assertTrue(MathUtils.isPrime(17), "Prime test");
        TestUtils.assertTrue(!MathUtils.isPrime(18), "Non-prime test");
        
        // Print results
        TestUtils.printResults();
    }
}
```

---

## Common Patterns

### Binary Search Template

```java
/**
 * Generic binary search template.
 */
public class BinarySearchTemplate {
    
    /**
     * Find minimum index satisfying condition.
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
     * Binary search on answer (monotonic predicate).
     */
    public static int binarySearchOnAnswer(int min, int max, Predicate<Integer> isValid) {
        var left = min;
        var right = max;
        var answer = min;
        
        while (left <= right) {
            var mid = left + (right - left) / 2;
            if (isValid.test(mid)) {
                answer = mid;
                right = mid - 1; // Try smaller
            } else {
                left = mid + 1; // Try larger
            }
        }
        
        return answer;
    }
}
```

### Sliding Window Template

```java
/**
 * Sliding window pattern templates.
 */
public class SlidingWindowTemplate {
    
    /**
     * Fixed-size window.
     */
    public static int fixedWindow(int[] arr, int k) {
        var maxSum = 0;
        var windowSum = 0;
        
        for (var i = 0; i < k; i++) {
            windowSum += arr[i];
        }
        maxSum = windowSum;
        
        for (var i = k; i < arr.length; i++) {
            windowSum += arr[i] - arr[i - k];
            maxSum = Math.max(maxSum, windowSum);
        }
        
        return maxSum;
    }
    
    /**
     * Variable-size window (expand/shrink).
     */
    public static int variableWindow(String s, int maxUnique) {
        var freq = new HashMap<Character, Integer>();
        var left = 0;
        var maxLen = 0;
        
        for (var right = 0; right < s.length(); right++) {
            freq.merge(s.charAt(right), 1, Integer::sum);
            
            while (freq.size() > maxUnique) {
                var leftChar = s.charAt(left);
                freq.merge(leftChar, -1, Integer::sum);
                if (freq.get(leftChar) == 0) {
                    freq.remove(leftChar);
                }
                left++;
            }
            
            maxLen = Math.max(maxLen, right - left + 1);
        }
        
        return maxLen;
    }
}
```

### Two Pointers Template

```java
/**
 * Two pointers pattern templates.
 */
public class TwoPointersTemplate {
    
    /**
     * Opposite direction (sorted array).
     */
    public static boolean twoSum(int[] arr, int target) {
        var left = 0;
        var right = arr.length - 1;
        
        while (left < right) {
            var sum = arr[left] + arr[right];
            if (sum == target) return true;
            if (sum < target) left++;
            else right--;
        }
        
        return false;
    }
    
    /**
     * Same direction (remove duplicates).
     */
    public static int removeDuplicates(int[] arr) {
        if (arr.length == 0) return 0;
        
        var write = 1;
        for (var read = 1; read < arr.length; read++) {
            if (arr[read] != arr[read - 1]) {
                arr[write++] = arr[read];
            }
        }
        
        return write;
    }
    
    /**
     * Fast/Slow (cycle detection).
     */
    public static boolean hasCycle(ListNode head) {
        if (head == null) return false;
        
        var slow = head;
        var fast = head;
        
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        
        return false;
    }
    
    private static class ListNode {
        int val;
        ListNode next;
    }
}
```

---

## Documentation Template

```java
/**
 * Standard documentation format for DSA implementations.
 * 
 * Problem: [Brief description]
 * 
 * Time Complexity: O(?)
 * Space Complexity: O(?)
 * 
 * Approach:
 * 1. [Step 1]
 * 2. [Step 2]
 * 
 * Example:
 * Input:  ?
 * Output: ?
 */
public class DocumentationTemplate {
    // Implementation here
}
```

---

*End of Utilities and Templates*

These helper classes and templates provide a solid foundation for implementing and testing DSA algorithms in Java 17+.