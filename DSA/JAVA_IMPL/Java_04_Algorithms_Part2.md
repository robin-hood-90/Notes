# Java 04: Algorithms Part 2

Complete Java 17+ implementations of dynamic programming, graph algorithms, string algorithms, and mathematical algorithms.

---

## Table of Contents

### Section O: Dynamic Programming
- [O.1 DP Fundamentals](#o-1-dp-fundamentals)
- [O.2 0/1 Knapsack](#o-2-0-1-knapsack)
- [O.3 Unbounded Knapsack](#o-3-unbounded-knapsack)
- [O.4 LCS Pattern](#o-4-lcs-pattern)
- [O.5 LIS Pattern](#o-5-lis-pattern)
- [O.6 Interval DP](#o-6-interval-dp)
- [O.7 Stock Trading DP](#o-7-stock-trading-dp)

### Section P: Graph Algorithms
- [P.1 Shortest Path](#p-1-shortest-path)
- [P.2 MST Algorithms](#p-2-mst-algorithms)
- [P.3 Topological Sort](#p-3-topological-sort)
- [P.4 SCC and Bridges](#p-4-scc-and-bridges)
- [P.5 A* Search](#p-5-a-search)
- [P.6 Johnson's Algorithm (APSP)](#p-6-johnson-s-algorithm-apsp)
- [P.7 SPFA](#p-7-spfa)

### Section Q: String Algorithms
- [Q.1 KMP Pattern Matching](#q-1-kmp-pattern-matching)
- [Q.2 Rolling Hash](#q-2-rolling-hash)
- [Q.3 Manacher's Algorithm](#q-3-manacher-s-algorithm)
- [Q.4 Z-Algorithm](#q-4-z-algorithm)
- [Q.5 Aho-Corasick](#q-5-aho-corasick)

### Section R: Mathematical Algorithms
- [R.1 Number Theory](#r-1-number-theory)
- [R.2 Fast Exponentiation](#r-2-fast-exponentiation)
- [R.3 Miller-Rabin Primality (64-bit)](#r-3-miller-rabin-primality-64-bit)
- [R.4 Chinese Remainder Theorem (CRT)](#r-4-chinese-remainder-theorem-crt)

---

## Section O: Dynamic Programming

---

### O.1 DP Fundamentals

**Concept:** Solve complex problems by breaking into overlapping subproblems, storing results.

**Visual (Fibonacci memoization):**
```
fib(5)
├── fib(4)
│   ├── fib(3) [calculated, reuse]
│   └── fib(2) [calculated, reuse]
└── fib(3) [reuse]

Top-down: Start from problem, recurse to base
Bottom-up: Start from base, build to solution
```

```java
/**
 * DP Patterns and Templates
 * Demonstrates top-down vs bottom-up approaches.
 */
public class DPTemplates {
    
    /**
     * Fibonacci - Top-down with memoization.
     */
    public static long fibTopDown(int n) {
        var memo = new Long[n + 1];
        return fibHelper(n, memo);
    }
    
    private static long fibHelper(int n, Long[] memo) {
        if (n <= 1) return n;
        if (memo[n] != null) return memo[n];
        
        memo[n] = fibHelper(n - 1, memo) + fibHelper(n - 2, memo);
        return memo[n];
    }
    
    /**
     * Fibonacci - Bottom-up with tabulation.
     */
    public static long fibBottomUp(int n) {
        if (n <= 1) return n;
        
        var dp = new long[n + 1];
        dp[0] = 0;
        dp[1] = 1;
        
        for (var i = 2; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        
        return dp[n];
    }
    
    /**
     * Fibonacci - Space optimized (O(1) space).
     */
    public static long fibOptimized(int n) {
        if (n <= 1) return n;
        
        var prev2 = 0L;
        var prev1 = 1L;
        
        for (var i = 2; i <= n; i++) {
            var current = prev1 + prev2;
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
    
    /**
     * Generic memoization template.
     */
    public static <T> T memoize(Function<T, T> func, T input, Map<T, T> memo) {
        if (memo.containsKey(input)) {
            return memo.get(input);
        }
        
        var result = func.apply(input);
        memo.put(input, result);
        return result;
    }
}
```

---

### O.2 0/1 Knapsack

**Concept:** Each item can be taken at most once. Maximize value within weight capacity.

**Visual:**
```
Items: (weight, value)
Item 0: (2, 3)    Item 1: (3, 4)    Item 2: (4, 5)    Item 3: (5, 6)

DP Table (capacity = 5):
       Capacity: 0   1   2   3   4   5
Item 0:            0   0   3   3   3   3
Item 1:            0   0   3   4   4   7
Item 2:            0   0   3   4   5   7
Item 3:            0   0   3   4   5   7

Max value = 7 (take items 0 and 1)
```

**Complexity:**
| Approach | Time | Space |
|----------|:----:|:-----:|
| Top-down | O(n×W) | O(n×W) |
| Bottom-up | O(n×W) | O(n×W) |
| Optimized | O(n×W) | O(W) |

```java
/**
 * 0/1 Knapsack - complete implementation with all approaches.
 */
public class Knapsack01 {
    
    public record Item(int weight, int value, String name) {}
    
    /**
     * Bottom-up with full table.
     */
    public static int solve(Item[] items, int capacity) {
        var n = items.length;
        var dp = new int[n + 1][capacity + 1];
        
        for (var i = 1; i <= n; i++) {
            var item = items[i - 1];
            
            for (var w = 0; w <= capacity; w++) {
                // Don't take item
                dp[i][w] = dp[i - 1][w];
                
                // Take item if possible
                if (item.weight <= w) {
                    dp[i][w] = Math.max(
                        dp[i][w],
                        dp[i - 1][w - item.weight] + item.value
                    );
                }
            }
        }
        
        return dp[n][capacity];
    }
    
    /**
     * Space optimized - uses only 1D array.
     */
    public static int solveOptimized(Item[] items, int capacity) {
        var dp = new int[capacity + 1];
        
        for (var item : items) {
            // Traverse backwards to avoid using updated values
            for (var w = capacity; w >= item.weight; w--) {
                dp[w] = Math.max(
                    dp[w],
                    dp[w - item.weight] + item.value
                );
            }
        }
        
        return dp[capacity];
    }
    
    /**
     * Return which items to take (reconstruct solution).
     */
    public static List<Item> solveWithSelection(Item[] items, int capacity) {
        var n = items.length;
        var dp = new int[n + 1][capacity + 1];
        
        // Fill DP table
        for (var i = 1; i <= n; i++) {
            var item = items[i - 1];
            for (var w = 0; w <= capacity; w++) {
                dp[i][w] = dp[i - 1][w];
                if (item.weight <= w) {
                    dp[i][w] = Math.max(
                        dp[i][w],
                        dp[i - 1][w - item.weight] + item.value
                    );
                }
            }
        }
        
        // Backtrack to find selected items
        var selected = new ArrayList<Item>();
        var w = capacity;
        
        for (var i = n; i > 0; i--) {
            if (dp[i][w] != dp[i - 1][w]) {
                // Item i-1 was taken
                selected.add(items[i - 1]);
                w -= items[i - 1].weight;
            }
        }
        
        Collections.reverse(selected);
        return selected;
    }
    
    /**
     * Subset Sum - special case where value = weight.
     */
    public static boolean subsetSum(int[] nums, int target) {
        var dp = new boolean[target + 1];
        dp[0] = true;
        
        for (var num : nums) {
            for (var t = target; t >= num; t--) {
                dp[t] = dp[t] || dp[t - num];
            }
        }
        
        return dp[target];
    }
    
    /**
     * Equal Sum Partition - can array be divided into two equal-sum subsets?
     */
    public static boolean canPartition(int[] nums) {
        var total = 0;
        for (var num : nums) total += num;
        
        if (total % 2 != 0) return false;
        
        return subsetSum(nums, total / 2);
    }
}
```

**Key Points:**
- Template for "select items with constraints" problems
- Space optimization: 2 rows or 1D array
- Backtracking reconstructs solution
- Variations: subset sum, partition, target sum

---

### O.3 Unbounded Knapsack

**Concept:** Items can be taken unlimited times.

```java
/**
 * Unbounded Knapsack - items can be taken multiple times.
 */
public class UnboundedKnapsack {
    
    public record Item(int weight, int value, String name) {}
    
    /**
     * Maximum value with unlimited items.
     */
    public static int solve(Item[] items, int capacity) {
        var dp = new int[capacity + 1];
        
        for (var w = 1; w <= capacity; w++) {
            for (var item : items) {
                if (item.weight <= w) {
                    dp[w] = Math.max(
                        dp[w],
                        dp[w - item.weight] + item.value
                    );
                }
            }
        }
        
        return dp[capacity];
    }
    
    /**
     * Coin Change - minimum coins to make amount.
     */
    public static int coinChange(int[] coins, int amount) {
        var dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1); // INF
        dp[0] = 0;
        
        for (var coin : coins) {
            for (var a = coin; a <= amount; a++) {
                dp[a] = Math.min(dp[a], dp[a - coin] + 1);
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
    
    /**
     * Coin Change - number of ways to make amount.
     */
    public static int coinChangeWays(int[] coins, int amount) {
        var dp = new int[amount + 1];
        dp[0] = 1;
        
        for (var coin : coins) {
            for (var a = coin; a <= amount; a++) {
                dp[a] += dp[a - coin];
            }
        }
        
        return dp[amount];
    }
    
    /**
     * Rod Cutting - maximize revenue from cutting rod.
     */
    public static int rodCutting(int[] prices, int n) {
        // prices[i] = price for rod of length i+1
        var dp = new int[n + 1];
        
        for (var len = 1; len <= n; len++) {
            for (var cut = 1; cut <= len; cut++) {
                dp[len] = Math.max(dp[len], prices[cut - 1] + dp[len - cut]);
            }
        }
        
        return dp[n];
    }
}
```

**Key Points:**
- Traverse forward (not backward like 0/1)
- Can take item multiple times
- Applications: coin change, rod cutting, integer break

---

### O.4 LCS Pattern

**Concept:** Find longest subsequence common to two strings.

**Visual:**
```
String 1: A B C B D A B
String 2: B D C A B A

LCS: B C B A (length 4)

DP Table:
      ""  B   D   C   A   B   A
""    0   0   0   0   0   0   0
A     0   0   0   0   1   1   1
B     0   1   1   1   1   2   2
C     0   1   1   2   2   2   2
B     0   1   1   2   2   3   3
D     0   1   2   2   2   3   3
A     0   1   2   2   3   3   4
B     0   1   2   2   3   4   4
```

```java
/**
 * Longest Common Subsequence (LCS) - classic 2D DP.
 */
public class LCS {
    
    /**
     * Standard LCS with full table.
     */
    public static int lcs(String s1, String s2) {
        var m = s1.length();
        var n = s2.length();
        var dp = new int[m + 1][n + 1];
        
        for (var i = 1; i <= m; i++) {
            for (var j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        
        return dp[m][n];
    }
    
    /**
     * Space optimized - uses 2 rows.
     */
    public static int lcsOptimized(String s1, String s2) {
        if (s1.length() < s2.length()) {
            var temp = s1;
            s1 = s2;
            s2 = temp;
        }
        
        var m = s1.length();
        var n = s2.length();
        var prev = new int[n + 1];
        var curr = new int[n + 1];
        
        for (var i = 1; i <= m; i++) {
            for (var j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    curr[j] = prev[j - 1] + 1;
                } else {
                    curr[j] = Math.max(prev[j], curr[j - 1]);
                }
            }
            // Swap arrays
            var temp = prev;
            prev = curr;
            curr = temp;
        }
        
        return prev[n];
    }
    
    /**
     * Reconstruct the actual LCS string.
     */
    public static String getLCS(String s1, String s2) {
        var m = s1.length();
        var n = s2.length();
        var dp = new int[m + 1][n + 1];
        
        // Fill table
        for (var i = 1; i <= m; i++) {
            for (var j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        
        // Backtrack to get string
        var sb = new StringBuilder();
        var i = m, j = n;
        
        while (i > 0 && j > 0) {
            if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                sb.append(s1.charAt(i - 1));
                i--;
                j--;
            } else if (dp[i - 1][j] > dp[i][j - 1]) {
                i--;
            } else {
                j--;
            }
        }
        
        return sb.reverse().toString();
    }
    
    /**
     * Edit Distance - minimum operations to convert s1 to s2.
     */
    public static int editDistance(String s1, String s2) {
        var m = s1.length();
        var n = s2.length();
        var dp = new int[m + 1][n + 1];
        
        // Base cases
        for (var i = 0; i <= m; i++) dp[i][0] = i;
        for (var j = 0; j <= n; j++) dp[0][j] = j;
        
        for (var i = 1; i <= m; i++) {
            for (var j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(
                        dp[i - 1][j - 1], // Replace
                        Math.min(
                            dp[i - 1][j],   // Delete
                            dp[i][j - 1]    // Insert
                        )
                    );
                }
            }
        }
        
        return dp[m][n];
    }
    
    /**
     * Distinct Subsequences - count ways s contains t as subsequence.
     */
    public static int distinctSubsequences(String s, String t) {
        var m = s.length();
        var n = t.length();
        var dp = new long[n + 1];
        dp[0] = 1;
        
        for (var i = 1; i <= m; i++) {
            for (var j = Math.min(i, n); j > 0; j--) {
                if (s.charAt(i - 1) == t.charAt(j - 1)) {
                    dp[j] += dp[j - 1];
                }
            }
        }
        
        return (int) dp[n];
    }
}
```

**Key Points:**
- Template for string comparison problems
- Space can be reduced to 2 rows or O(min(m,n))
- Variations: edit distance, distinct subsequences, wildcard matching

---

### O.5 LIS Pattern

**Concept:** Find longest increasing subsequence in array.

**Visual:**
```
Array: [10, 9, 2, 5, 3, 7, 101, 18]

LIS: [2, 3, 7, 18] (length 4)

DP Approach (O(n²)):
i=0: [10]                      len=1
i=1: [9]                       len=1
i=2: [2]                       len=1
i=3: [2, 5]                    len=2
i=4: [2, 3]                    len=2
i=5: [2, 3, 7]                 len=3
i=6: [2, 3, 7, 101]            len=4
i=7: [2, 3, 7, 18]             len=4

Patience Sorting (O(n log n)):
Piles: [2] [3] [7] [18]
              [5]    [101]
              [9]
              [10]
```

```java
/**
 * Longest Increasing Subsequence (LIS) - O(n²) and O(n log n).
 */
public class LIS {
    
    /**
     * O(n²) DP solution.
     */
    public static int lengthOfLIS(int[] nums) {
        if (nums.length == 0) return 0;
        
        var n = nums.length;
        var dp = new int[n];
        Arrays.fill(dp, 1);
        
        var maxLen = 1;
        
        for (var i = 1; i < n; i++) {
            for (var j = 0; j < i; j++) {
                if (nums[i] > nums[j]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
            maxLen = Math.max(maxLen, dp[i]);
        }
        
        return maxLen;
    }
    
    /**
     * O(n log n) using patience sorting / binary search.
     */
    public static int lengthOfLISOptimized(int[] nums) {
        var tails = new ArrayList<Integer>();
        
        for (var num : nums) {
            // Binary search for insertion point
            var idx = Collections.binarySearch(tails, num);
            if (idx < 0) idx = -idx - 1;
            
            if (idx == tails.size()) {
                tails.add(num);
            } else {
                tails.set(idx, num);
            }
        }
        
        return tails.size();
    }
    
    /**
     * Return the actual LIS sequence.
     */
    public static List<Integer> getLIS(int[] nums) {
        var n = nums.length;
        var dp = new int[n];
        var parent = new int[n]; // Track predecessors
        Arrays.fill(dp, 1);
        Arrays.fill(parent, -1);
        
        var maxLen = 1;
        var maxIdx = 0;
        
        for (var i = 1; i < n; i++) {
            for (var j = 0; j < i; j++) {
                if (nums[i] > nums[j] && dp[i] < dp[j] + 1) {
                    dp[i] = dp[j] + 1;
                    parent[i] = j;
                }
            }
            if (dp[i] > maxLen) {
                maxLen = dp[i];
                maxIdx = i;
            }
        }
        
        // Reconstruct LIS
        var lis = new LinkedList<Integer>();
        while (maxIdx != -1) {
            lis.addFirst(nums[maxIdx]);
            maxIdx = parent[maxIdx];
        }
        
        return lis;
    }
    
    /**
     * Number of Longest Increasing Subsequences.
     */
    public static int numberOfLIS(int[] nums) {
        var n = nums.length;
        var length = new int[n];
        var count = new int[n];
        Arrays.fill(length, 1);
        Arrays.fill(count, 1);
        
        var maxLen = 1;
        var result = 0;
        
        for (var i = 0; i < n; i++) {
            for (var j = 0; j < i; j++) {
                if (nums[i] > nums[j]) {
                    if (length[j] + 1 > length[i]) {
                        length[i] = length[j] + 1;
                        count[i] = count[j];
                    } else if (length[j] + 1 == length[i]) {
                        count[i] += count[j];
                    }
                }
            }
            maxLen = Math.max(maxLen, length[i]);
        }
        
        for (var i = 0; i < n; i++) {
            if (length[i] == maxLen) {
                result += count[i];
            }
        }
        
        return result;
    }
    
    /**
     * Russian Doll Envelopes - 2D LIS variant.
     */
    public static int maxEnvelopes(int[][] envelopes) {
        // Sort by width ascending, height descending for same width
        Arrays.sort(envelopes, (a, b) -> {
            if (a[0] != b[0]) return Integer.compare(a[0], b[0]);
            return Integer.compare(b[1], a[1]);
        });
        
        // LIS on heights
        var tails = new ArrayList<Integer>();
        
        for (var env : envelopes) {
            var height = env[1];
            var idx = Collections.binarySearch(tails, height);
            if (idx < 0) idx = -idx - 1;
            
            if (idx == tails.size()) {
                tails.add(height);
            } else {
                tails.set(idx, height);
            }
        }
        
        return tails.size();
    }
}
```

**Key Points:**
- O(n²) for understanding, O(n log n) for interviews
- Patience sorting with binary search
- Track parent pointers to reconstruct sequence
- Variations: bitonic, sum, envelopes

---

### O.6 Interval DP

**Concept:** DP on intervals - burst balloons, matrix chain, stone games.

```java
/**
 * Interval DP - problems on subarrays/substrings.
 */
public class IntervalDP {
    
    /**
     * Matrix Chain Multiplication - min cost to multiply chain.
     */
    public static int matrixChainOrder(int[] dims) {
        var n = dims.length - 1; // Number of matrices
        var dp = new int[n][n];
        
        // Chain length from 2 to n
        for (var len = 2; len <= n; len++) {
            for (var i = 0; i <= n - len; i++) {
                var j = i + len - 1;
                dp[i][j] = Integer.MAX_VALUE;
                
                for (var k = i; k < j; k++) {
                    var cost = dp[i][k] + dp[k + 1][j] 
                             + dims[i] * dims[k + 1] * dims[j + 1];
                    dp[i][j] = Math.min(dp[i][j], cost);
                }
            }
        }
        
        return dp[0][n - 1];
    }
    
    /**
     * Burst Balloons - max coins.
     */
    public static int maxCoins(int[] nums) {
        var n = nums.length;
        var balloons = new int[n + 2];
        balloons[0] = 1;
        balloons[n + 1] = 1;
        System.arraycopy(nums, 0, balloons, 1, n);
        
        var dp = new int[n + 2][n + 2];
        
        for (var len = 1; len <= n; len++) {
            for (var i = 1; i <= n - len + 1; i++) {
                var j = i + len - 1;
                for (var k = i; k <= j; k++) {
                    dp[i][j] = Math.max(dp[i][j],
                        balloons[i - 1] * balloons[k] * balloons[j + 1]
                        + dp[i][k - 1] + dp[k + 1][j]
                    );
                }
            }
        }
        
        return dp[1][n];
    }
    
    /**
     * Stone Game - Alice and Bob take stones from ends.
     */
    public static boolean stoneGame(int[] piles) {
        var n = piles.length;
        var dp = new int[n][n];
        
        // Base case: single pile
        for (var i = 0; i < n; i++) {
            dp[i][i] = piles[i];
        }
        
        for (var len = 2; len <= n; len++) {
            for (var i = 0; i <= n - len; i++) {
                var j = i + len - 1;
                dp[i][j] = Math.max(
                    piles[i] - dp[i + 1][j],
                    piles[j] - dp[i][j - 1]
                );
            }
        }
        
        return dp[0][n - 1] > 0;
    }
    
    /**
     * Longest Palindromic Substring.
     */
    public static String longestPalindrome(String s) {
        var n = s.length();
        var dp = new boolean[n][n];
        var start = 0;
        var maxLen = 1;
        
        // Single characters are palindromes
        for (var i = 0; i < n; i++) {
            dp[i][i] = true;
        }
        
        // Check for length 2
        for (var i = 0; i < n - 1; i++) {
            if (s.charAt(i) == s.charAt(i + 1)) {
                dp[i][i + 1] = true;
                start = i;
                maxLen = 2;
            }
        }
        
        // Check for lengths > 2
        for (var len = 3; len <= n; len++) {
            for (var i = 0; i <= n - len; i++) {
                var j = i + len - 1;
                if (s.charAt(i) == s.charAt(j) && dp[i + 1][j - 1]) {
                    dp[i][j] = true;
                    start = i;
                    maxLen = len;
                }
            }
        }
        
        return s.substring(start, start + maxLen);
    }
}
```

---

### O.7 Stock Trading DP

**Concept:** State machine DP for buy/sell stock problems.

```java
/**
 * Stock Trading - state machine DP pattern.
 */
public class StockTrading {
    
    /**
     * One transaction allowed.
     */
    public static int maxProfitOneTransaction(int[] prices) {
        if (prices.length == 0) return 0;
        
        var minPrice = prices[0];
        var maxProfit = 0;
        
        for (var price : prices) {
            minPrice = Math.min(minPrice, price);
            maxProfit = Math.max(maxProfit, price - minPrice);
        }
        
        return maxProfit;
    }
    
    /**
     * Unlimited transactions.
     */
    public static int maxProfitUnlimited(int[] prices) {
        var profit = 0;
        
        for (var i = 1; i < prices.length; i++) {
            if (prices[i] > prices[i - 1]) {
                profit += prices[i] - prices[i - 1];
            }
        }
        
        return profit;
    }
    
    /**
     * At most k transactions.
     */
    public static int maxProfitKTransactions(int[] prices, int k) {
        var n = prices.length;
        
        // Optimization: unlimited transactions case
        if (k >= n / 2) {
            return maxProfitUnlimited(prices);
        }
        
        var dp = new int[k + 1][n];
        
        for (var t = 1; t <= k; t++) {
            var maxDiff = -prices[0];
            
            for (var d = 1; d < n; d++) {
                dp[t][d] = Math.max(dp[t][d - 1], prices[d] + maxDiff);
                maxDiff = Math.max(maxDiff, dp[t - 1][d] - prices[d]);
            }
        }
        
        return dp[k][n - 1];
    }
    
    /**
     * With cooldown (1 day after sell).
     */
    public static int maxProfitWithCooldown(int[] prices) {
        if (prices.length == 0) return 0;
        
        var n = prices.length;
        var hold = new int[n];
        var notHold = new int[n];
        
        hold[0] = -prices[0];
        notHold[0] = 0;
        
        for (var i = 1; i < n; i++) {
            hold[i] = Math.max(hold[i - 1], 
                             (i >= 2 ? notHold[i - 2] : 0) - prices[i]);
            notHold[i] = Math.max(notHold[i - 1], hold[i - 1] + prices[i]);
        }
        
        return notHold[n - 1];
    }
    
    /**
     * With transaction fee.
     */
    public static int maxProfitWithFee(int[] prices, int fee) {
        var hold = -prices[0];
        var notHold = 0;
        
        for (var i = 1; i < prices.length; i++) {
            hold = Math.max(hold, notHold - prices[i]);
            notHold = Math.max(notHold, hold + prices[i] - fee);
        }
        
        return notHold;
    }
}
```

---

## Section P: Graph Algorithms

---

### P.1 Shortest Path

**Concept:** Find shortest paths in graphs using various algorithms.

```java
/**
 * Graph Algorithms - Dijkstra, Bellman-Ford, Floyd-Warshall.
 */
public class GraphAlgorithms {
    
    private record Edge(int to, int weight) {}
    private record Node(int vertex, int dist) implements Comparable<Node> {
        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.dist, other.dist);
        }
    }
    
    /**
     * Dijkstra's Algorithm - shortest path from source.
     * Time: O(E log V), Space: O(V)
     */
    public static int[] dijkstra(List<List<Edge>> graph, int source) {
        var n = graph.size();
        var dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        var pq = new PriorityQueue<Node>();
        pq.offer(new Node(source, 0));
        
        while (!pq.isEmpty()) {
            var curr = pq.poll();
            
            // Skip if already processed
            if (curr.dist > dist[curr.vertex]) continue;
            
            for (var edge : graph.get(curr.vertex)) {
                var newDist = dist[curr.vertex] + edge.weight;
                
                if (newDist < dist[edge.to]) {
                    dist[edge.to] = newDist;
                    pq.offer(new Node(edge.to, newDist));
                }
            }
        }
        
        return dist;
    }
    
    /**
     * Bellman-Ford - handles negative weights.
     * Time: O(V×E), Space: O(V)
     */
    public static int[] bellmanFord(int[][] edges, int n, int source) {
        var dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        // Relax all edges V-1 times
        for (var i = 0; i < n - 1; i++) {
            for (var edge : edges) {
                var u = edge[0], v = edge[1], w = edge[2];
                if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                }
            }
        }
        
        // Check for negative cycles
        for (var edge : edges) {
            var u = edge[0], v = edge[1], w = edge[2];
            if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                throw new IllegalStateException("Negative cycle detected");
            }
        }
        
        return dist;
    }
    
    /**
     * Floyd-Warshall - all pairs shortest paths.
     * Time: O(V³), Space: O(V²)
     */
    public static int[][] floydWarshall(int[][] graph) {
        var n = graph.length;
        var dist = new int[n][n];
        
        // Initialize
        for (var i = 0; i < n; i++) {
            for (var j = 0; j < n; j++) {
                dist[i][j] = graph[i][j];
            }
        }
        
        // Dynamic programming
        for (var k = 0; k < n; k++) {
            for (var i = 0; i < n; i++) {
                for (var j = 0; j < n; j++) {
                    if (dist[i][k] != Integer.MAX_VALUE && 
                        dist[k][j] != Integer.MAX_VALUE &&
                        dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        
        return dist;
    }
    
    /**
     * 0-1 BFS - for graphs with weights 0 or 1.
     * Time: O(V + E), Space: O(V)
     */
    public static int[] zeroOneBFS(List<List<Edge>> graph, int source) {
        var n = graph.size();
        var dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        var deque = new ArrayDeque<Integer>();
        deque.offerFirst(source);
        
        while (!deque.isEmpty()) {
            var u = deque.pollFirst();
            
            for (var edge : graph.get(u)) {
                var newDist = dist[u] + edge.weight;
                
                if (newDist < dist[edge.to]) {
                    dist[edge.to] = newDist;
                    
                    if (edge.weight == 0) {
                        deque.offerFirst(edge.to);
                    } else {
                        deque.offerLast(edge.to);
                    }
                }
            }
        }
        
        return dist;
    }
}
```

---

### P.2 MST Algorithms

**Concept:** Find minimum spanning tree connecting all vertices.

```java
/**
 * Minimum Spanning Tree - Kruskal's and Prim's algorithms.
 */
public class MST {
    
    private record Edge(int from, int to, int weight) 
        implements Comparable<Edge> {
        @Override
        public int compareTo(Edge other) {
            return Integer.compare(this.weight, other.weight);
        }
    }
    
    /**
     * Kruskal's Algorithm - sort edges, add if no cycle.
     * Time: O(E log E), Space: O(V)
     */
    public static List<Edge> kruskal(int n, List<Edge> edges) {
        Collections.sort(edges);
        
        var uf = new UnionFind(n);
        var mst = new ArrayList<Edge>();
        
        for (var edge : edges) {
            if (uf.union(edge.from, edge.to)) {
                mst.add(edge);
                if (mst.size() == n - 1) break;
            }
        }
        
        return mst;
    }
    
    /**
     * Prim's Algorithm - grow tree from vertex.
     * Time: O(E log V), Space: O(V)
     */
    public static List<Edge> prim(List<List<Edge>> graph, int start) {
        var n = graph.size();
        var visited = new boolean[n];
        var mst = new ArrayList<Edge>();
        var pq = new PriorityQueue<Edge>();
        
        visited[start] = true;
        
        // Add all edges from start
        for (var edge : graph.get(start)) {
            pq.offer(new Edge(start, edge.to, edge.weight));
        }
        
        while (!pq.isEmpty() && mst.size() < n - 1) {
            var edge = pq.poll();
            
            if (visited[edge.to]) continue;
            
            visited[edge.to] = true;
            mst.add(edge);
            
            for (var next : graph.get(edge.to)) {
                if (!visited[next.to]) {
                    pq.offer(new Edge(edge.to, next.to, next.weight));
                }
            }
        }
        
        return mst;
    }
    
    /**
     * Simple Union-Find for Kruskal's.
     */
    private static class UnionFind {
        int[] parent, rank;
        
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (var i = 0; i < n; i++) parent[i] = i;
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            var px = find(x), py = find(y);
            if (px == py) return false;
            
            if (rank[px] < rank[py]) {
                parent[px] = py;
            } else if (rank[px] > rank[py]) {
                parent[py] = px;
            } else {
                parent[py] = px;
                rank[px]++;
            }
            return true;
        }
    }
}
```

---

## Section P: Graph Algorithms (continued)

---

### P.3 Topological Sort

**Concept:** Order vertices in a DAG so every directed edge `u -> v` goes from left to right.

```java
import java.util.*;

public class TopologicalSort {

    /**
     * Kahn's algorithm (BFS on in-degrees).
     * Returns empty array if graph has a cycle.
     */
    public static int[] kahn(int n, int[][] edges) {
        var g = new ArrayList<Integer>(n);
        var adj = new ArrayList<ArrayList<Integer>>(n);
        for (var i = 0; i < n; i++) adj.add(new ArrayList<>());

        var indeg = new int[n];
        for (var e : edges) {
            var u = e[0];
            var v = e[1];
            adj.get(u).add(v);
            indeg[v]++;
        }

        var q = new ArrayDeque<Integer>();
        for (var i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);

        var order = new int[n];
        var idx = 0;
        while (!q.isEmpty()) {
            var u = q.poll();
            order[idx++] = u;
            for (var v : adj.get(u)) {
                if (--indeg[v] == 0) q.add(v);
            }
        }

        if (idx != n) return new int[0];
        return order;
    }

    /**
     * DFS-based topo sort.
     * Returns empty array if a back-edge (cycle) is found.
     */
    public static int[] dfsTopo(int n, int[][] edges) {
        var adj = new ArrayList<ArrayList<Integer>>(n);
        for (var i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (var e : edges) adj.get(e[0]).add(e[1]);

        var state = new int[n]; // 0=unvisited,1=visiting,2=done
        var order = new int[n];
        var idx = n;

        for (var i = 0; i < n; i++) {
            if (state[i] == 0) {
                idx = dfs(i, adj, state, order, idx);
                if (idx < 0) return new int[0];
            }
        }
        return order;
    }

    private static int dfs(int u, List<? extends List<Integer>> adj, int[] state, int[] order, int idx) {
        state[u] = 1;
        for (var v : adj.get(u)) {
            if (state[v] == 1) return -1; // cycle
            if (state[v] == 0) {
                idx = dfs(v, adj, state, order, idx);
                if (idx < 0) return -1;
            }
        }
        state[u] = 2;
        order[--idx] = u;
        return idx;
    }
}
```

---

### P.4 SCC and Bridges

**Concepts:**
- SCC (Strongly Connected Components): in a directed graph, nodes mutually reachable.
- Bridges: in an undirected graph, edges whose removal increases #components.

```java
import java.util.*;

public class SCCAndBridges {

    /**
     * Kosaraju SCC: O(n+m).
     * Returns component id for each node (0..cc-1).
     */
    public static int[] kosarajuScc(int n, int[][] edges) {
        var g = new ArrayList<ArrayList<Integer>>(n);
        var gr = new ArrayList<ArrayList<Integer>>(n);
        for (var i = 0; i < n; i++) {
            g.add(new ArrayList<>());
            gr.add(new ArrayList<>());
        }
        for (var e : edges) {
            var u = e[0];
            var v = e[1];
            g.get(u).add(v);
            gr.get(v).add(u);
        }

        var vis = new boolean[n];
        var order = new int[n];
        var idx = 0;
        for (var i = 0; i < n; i++) if (!vis[i]) idx = dfs1(i, g, vis, order, idx);

        Arrays.fill(vis, false);
        var comp = new int[n];
        var cc = 0;
        for (var i = n - 1; i >= 0; i--) {
            var v = order[i];
            if (!vis[v]) {
                dfs2(v, gr, vis, comp, cc);
                cc++;
            }
        }
        return comp;
    }

    private static int dfs1(int u, List<? extends List<Integer>> g, boolean[] vis, int[] order, int idx) {
        vis[u] = true;
        for (var v : g.get(u)) if (!vis[v]) idx = dfs1(v, g, vis, order, idx);
        order[idx++] = u;
        return idx;
    }

    private static void dfs2(int u, List<? extends List<Integer>> gr, boolean[] vis, int[] comp, int id) {
        vis[u] = true;
        comp[u] = id;
        for (var v : gr.get(u)) if (!vis[v]) dfs2(v, gr, vis, comp, id);
    }

    /**
     * Bridges in an undirected graph: O(n+m).
     * edgesUndir: list of edges [u,v] (0-indexed). Graph may be disconnected.
     * Returns list of bridges as int[]{u,v} with original endpoints.
     */
    public static List<int[]> bridges(int n, int[][] edgesUndir) {
        var adj = new ArrayList<ArrayList<int[]>>(n);
        for (var i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (var i = 0; i < edgesUndir.length; i++) {
            var u = edgesUndir[i][0];
            var v = edgesUndir[i][1];
            adj.get(u).add(new int[]{v, i});
            adj.get(v).add(new int[]{u, i});
        }

        var tin = new int[n];
        var low = new int[n];
        Arrays.fill(tin, -1);
        var timer = 0;
        var res = new ArrayList<int[]>();

        for (var i = 0; i < n; i++) {
            if (tin[i] == -1) {
                timer = dfsBridge(i, -1, -1, adj, tin, low, timer, edgesUndir, res);
            }
        }
        return res;
    }

    private static int dfsBridge(
        int u,
        int p,
        int pEdge,
        List<? extends List<int[]>> adj,
        int[] tin,
        int[] low,
        int timer,
        int[][] edges,
        List<int[]> out
    ) {
        tin[u] = low[u] = timer++;
        for (var nxt : adj.get(u)) {
            var v = nxt[0];
            var eId = nxt[1];
            if (eId == pEdge) continue;
            if (tin[v] != -1) {
                low[u] = Math.min(low[u], tin[v]);
            } else {
                timer = dfsBridge(v, u, eId, adj, tin, low, timer, edges, out);
                low[u] = Math.min(low[u], low[v]);
                if (low[v] > tin[u]) {
                    out.add(new int[]{edges[eId][0], edges[eId][1]});
                }
            }
        }
        return timer;
    }
}
```

---

### P.5 A* Search

```java
import java.util.*;
import java.util.function.IntUnaryOperator;

public class AStar {

    public record Edge(int to, int w) {}
    private record State(int v, long f, long g) implements Comparable<State> {
        @Override public int compareTo(State o) { return Long.compare(this.f, o.f); }
    }

    /**
     * A* shortest path from s to t.
     * heuristic h(v) must be admissible (never overestimates) for optimality.
     * Returns dist[t] (or Long.MAX_VALUE if unreachable).
     */
    public static long shortestPath(List<Edge>[] g, int s, int t, IntUnaryOperator h) {
        var n = g.length;
        var dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[s] = 0;

        var pq = new PriorityQueue<State>();
        pq.add(new State(s, h.applyAsInt(s), 0));

        while (!pq.isEmpty()) {
            var cur = pq.poll();
            var v = cur.v;
            if (cur.g != dist[v]) continue;
            if (v == t) return dist[t];
            for (var e : g[v]) {
                var nd = dist[v] + e.w;
                if (nd < dist[e.to]) {
                    dist[e.to] = nd;
                    var f = nd + (long) h.applyAsInt(e.to);
                    pq.add(new State(e.to, f, nd));
                }
            }
        }
        return Long.MAX_VALUE;
    }
}
```

---

### P.6 Johnson's Algorithm (APSP)

```java
import java.util.*;

public class JohnsonAPSP {
    public record E(int u, int v, int w) {}
    public record Adj(int to, int w) {}

    /**
     * Johnson's APSP for directed graphs with possible negative edges (no negative cycles).
     * Returns dist matrix (n x n), where dist[i][j] can be Long.MAX_VALUE if unreachable.
     */
    public static long[][] allPairs(int n, List<E> edges) {
        // Bellman-Ford from super source
        var h = new long[n];
        Arrays.fill(h, 0);
        for (var it = 0; it < n - 1; it++) {
            var changed = false;
            for (var e : edges) {
                if (h[e.u] + e.w < h[e.v]) {
                    h[e.v] = h[e.u] + e.w;
                    changed = true;
                }
            }
            if (!changed) break;
        }
        for (var e : edges) {
            if (h[e.u] + e.w < h[e.v]) {
                throw new IllegalStateException("Negative cycle");
            }
        }

        @SuppressWarnings("unchecked")
        var g = (List<Adj>[]) new List[n];
        for (var i = 0; i < n; i++) g[i] = new ArrayList<>();
        for (var e : edges) {
            // reweight to non-negative
            var w2 = (int) (e.w + h[e.u] - h[e.v]);
            g[e.u].add(new Adj(e.v, w2));
        }

        var dist = new long[n][n];
        for (var i = 0; i < n; i++) Arrays.fill(dist[i], Long.MAX_VALUE);
        for (var s = 0; s < n; s++) {
            var d2 = dijkstra(g, s);
            for (var v = 0; v < n; v++) {
                if (d2[v] == Long.MAX_VALUE) continue;
                // un-reweight
                dist[s][v] = d2[v] - h[s] + h[v];
            }
        }
        return dist;
    }

    private record Node(int v, long d) implements Comparable<Node> {
        @Override public int compareTo(Node o) { return Long.compare(this.d, o.d); }
    }

    private static long[] dijkstra(List<Adj>[] g, int s) {
        var n = g.length;
        var dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[s] = 0;
        var pq = new PriorityQueue<Node>();
        pq.add(new Node(s, 0));
        while (!pq.isEmpty()) {
            var cur = pq.poll();
            if (cur.d != dist[cur.v]) continue;
            for (var e : g[cur.v]) {
                var nd = cur.d + e.w;
                if (nd < dist[e.to]) {
                    dist[e.to] = nd;
                    pq.add(new Node(e.to, nd));
                }
            }
        }
        return dist;
    }
}
```

---

### P.7 SPFA

```java
import java.util.*;

public class SPFA {
    public record Edge(int to, int w) {}

    /**
     * SPFA: can be fast in practice, O(VE) worst-case.
     * Throws if a negative cycle is detected reachable from source.
     */
    public static long[] shortestPaths(List<Edge>[] g, int s) {
        var n = g.length;
        var dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[s] = 0;

        var inQ = new boolean[n];
        var cnt = new int[n];
        var q = new ArrayDeque<Integer>();
        q.add(s);
        inQ[s] = true;

        while (!q.isEmpty()) {
            var u = q.poll();
            inQ[u] = false;
            var du = dist[u];
            if (du == Long.MAX_VALUE) continue;
            for (var e : g[u]) {
                var nd = du + e.w;
                if (nd < dist[e.to]) {
                    dist[e.to] = nd;
                    if (!inQ[e.to]) {
                        q.add(e.to);
                        inQ[e.to] = true;
                        if (++cnt[e.to] >= n) throw new IllegalStateException("Negative cycle");
                    }
                }
            }
        }
        return dist;
    }
}
```

---

## Section Q: String Algorithms

---

### Q.1 KMP Pattern Matching

```java
import java.util.*;

public class KMP {

    /**
     * Builds LPS array for pattern p.
     * lps[i] = length of longest proper prefix == suffix for p[0..i].
     */
    public static int[] lps(String p) {
        var m = p.length();
        var lps = new int[m];
        for (int i = 1, len = 0; i < m; ) {
            if (p.charAt(i) == p.charAt(len)) {
                lps[i++] = ++len;
            } else if (len > 0) {
                len = lps[len - 1];
            } else {
                lps[i++] = 0;
            }
        }
        return lps;
    }

    /**
     * Returns all match start indices of pattern p in text t.
     */
    public static List<Integer> search(String t, String p) {
        var n = t.length();
        var m = p.length();
        if (m == 0) return List.of();

        var lps = lps(p);
        var res = new ArrayList<Integer>();
        for (int i = 0, j = 0; i < n; ) {
            if (t.charAt(i) == p.charAt(j)) {
                i++; j++;
                if (j == m) {
                    res.add(i - m);
                    j = lps[j - 1];
                }
            } else if (j > 0) {
                j = lps[j - 1];
            } else {
                i++;
            }
        }
        return res;
    }
}
```

---

### Q.2 Rolling Hash

```java
import java.util.*;

public class RollingHash {
    // CP defaults; adjust if needed.
    static final long MOD1 = 1_000_000_007L;
    static final long MOD2 = 1_000_000_009L;
    static final long BASE = 911382323L;

    static final class Hasher {
        final int n;
        final long[] p1, p2, h1, h2;

        Hasher(String s) {
            this.n = s.length();
            p1 = new long[n + 1];
            p2 = new long[n + 1];
            h1 = new long[n + 1];
            h2 = new long[n + 1];
            p1[0] = 1; p2[0] = 1;
            for (var i = 0; i < n; i++) {
                var c = (long) s.charAt(i);
                p1[i + 1] = (p1[i] * BASE) % MOD1;
                p2[i + 1] = (p2[i] * BASE) % MOD2;
                h1[i + 1] = (h1[i] * BASE + c) % MOD1;
                h2[i + 1] = (h2[i] * BASE + c) % MOD2;
            }
        }

        // Hash of substring [l, r) (0-indexed, r exclusive)
        long[] get(int l, int r) {
            var x1 = (h1[r] - (h1[l] * p1[r - l]) % MOD1 + MOD1) % MOD1;
            var x2 = (h2[r] - (h2[l] * p2[r - l]) % MOD2 + MOD2) % MOD2;
            return new long[]{x1, x2};
        }
    }

    public static boolean equals(Hasher a, int al, int ar, Hasher b, int bl, int br) {
        if (ar - al != br - bl) return false;
        var ha = a.get(al, ar);
        var hb = b.get(bl, br);
        return ha[0] == hb[0] && ha[1] == hb[1];
    }
}
```

---

### Q.3 Manacher's Algorithm

```java
public class Manacher {

    /**
     * Returns array d1 where d1[i] = radius of odd palindrome centered at i.
     * Odd palindrome length = 2*d1[i]-1.
     */
    public static int[] oddPalRadii(String s) {
        var n = s.length();
        var d1 = new int[n];
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            var k = (i > r) ? 1 : Math.min(d1[l + r - i], r - i + 1);
            while (i - k >= 0 && i + k < n && s.charAt(i - k) == s.charAt(i + k)) k++;
            d1[i] = k;
            if (i + k - 1 > r) {
                l = i - k + 1;
                r = i + k - 1;
            }
        }
        return d1;
    }

    /**
     * Returns array d2 where d2[i] = radius of even palindrome centered between i-1 and i.
     * Even palindrome length = 2*d2[i].
     */
    public static int[] evenPalRadii(String s) {
        var n = s.length();
        var d2 = new int[n];
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            var k = (i > r) ? 0 : Math.min(d2[l + r - i + 1], r - i + 1);
            while (i - k - 1 >= 0 && i + k < n && s.charAt(i - k - 1) == s.charAt(i + k)) k++;
            d2[i] = k;
            if (i + k - 1 > r) {
                l = i - k;
                r = i + k - 1;
            }
        }
        return d2;
    }

    public static int longestPalindromeLength(String s) {
        var d1 = oddPalRadii(s);
        var d2 = evenPalRadii(s);
        var best = 0;
        for (var x : d1) best = Math.max(best, 2 * x - 1);
        for (var x : d2) best = Math.max(best, 2 * x);
        return best;
    }
}
```

---

### Q.4 Z-Algorithm

```java
import java.util.*;

public class ZAlgorithm {

    // z[i] = length of longest substring starting at i that is also a prefix of s.
    public static int[] z(String s) {
        var n = s.length();
        var z = new int[n];
        for (int i = 1, l = 0, r = 0; i < n; i++) {
            if (i <= r) z[i] = Math.min(r - i + 1, z[i - l]);
            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;
            if (i + z[i] - 1 > r) {
                l = i;
                r = i + z[i] - 1;
            }
        }
        return z;
    }

    public static List<Integer> findAll(String text, String pattern) {
        if (pattern.isEmpty()) return List.of();
        var s = pattern + "$" + text;
        var z = z(s);
        var res = new ArrayList<Integer>();
        var m = pattern.length();
        for (var i = m + 1; i < s.length(); i++) {
            if (z[i] >= m) res.add(i - (m + 1));
        }
        return res;
    }
}
```

---

### Q.5 Aho-Corasick

```java
import java.util.*;

public class AhoCorasick {
    static final int ALPHA = 26;

    static final class Node {
        int[] next = new int[ALPHA];
        int link;
        int out; // number of patterns ending here
        Node() { Arrays.fill(next, -1); }
    }

    final ArrayList<Node> t = new ArrayList<>();

    public AhoCorasick() {
        t.add(new Node());
        t.get(0).link = 0;
    }

    public void add(String s) {
        var v = 0;
        for (var i = 0; i < s.length(); i++) {
            var c = s.charAt(i) - 'a';
            if (t.get(v).next[c] == -1) {
                t.get(v).next[c] = t.size();
                t.add(new Node());
            }
            v = t.get(v).next[c];
        }
        t.get(v).out++;
    }

    public void build() {
        var q = new ArrayDeque<Integer>();
        for (var c = 0; c < ALPHA; c++) {
            var u = t.get(0).next[c];
            if (u != -1) {
                t.get(u).link = 0;
                q.add(u);
            } else {
                t.get(0).next[c] = 0;
            }
        }

        while (!q.isEmpty()) {
            var v = q.poll();
            var link = t.get(v).link;
            t.get(v).out += t.get(link).out;
            for (var c = 0; c < ALPHA; c++) {
                var u = t.get(v).next[c];
                if (u != -1) {
                    t.get(u).link = t.get(link).next[c];
                    q.add(u);
                } else {
                    t.get(v).next[c] = t.get(link).next[c];
                }
            }
        }
    }

    // returns total number of pattern occurrences in text (counts duplicates if added multiple times)
    public long matchCount(String text) {
        long res = 0;
        var v = 0;
        for (var i = 0; i < text.length(); i++) {
            var c = text.charAt(i) - 'a';
            if (c < 0 || c >= ALPHA) throw new IllegalArgumentException("Only lowercase a-z supported");
            v = t.get(v).next[c];
            res += t.get(v).out;
        }
        return res;
    }
}
```

---

## Section R: Mathematical Algorithms

---

### R.1 Number Theory

```java
import java.util.*;

public class NumberTheory {

    public static long gcd(long a, long b) {
        while (b != 0) {
            var t = a % b;
            a = b;
            b = t;
        }
        return Math.abs(a);
    }

    // returns {g, x, y} such that a*x + b*y = g = gcd(a,b)
    public static long[] extGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        var r = extGcd(b, a % b);
        var g = r[0];
        var x = r[2];
        var y = r[1] - (a / b) * r[2];
        return new long[]{g, x, y};
    }

    public static long modNormalize(long x, long mod) {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }

    public static long modInverse(long a, long mod) {
        var r = extGcd(a, mod);
        if (Math.abs(r[0]) != 1) throw new IllegalArgumentException("Inverse does not exist");
        return modNormalize(r[1], mod);
    }

    /**
     * Sieve primes up to n (inclusive).
     */
    public static int[] primesUpTo(int n) {
        if (n < 1) return new int[0];
        var isPrime = new boolean[n + 1];
        Arrays.fill(isPrime, true);
        if (n >= 0) isPrime[0] = false;
        if (n >= 1) isPrime[1] = false;
        for (long i = 2; i * i <= n; i++) {
            if (!isPrime[(int) i]) continue;
            for (long j = i * i; j <= n; j += i) isPrime[(int) j] = false;
        }
        var cnt = 0;
        for (var i = 2; i <= n; i++) if (isPrime[i]) cnt++;
        var primes = new int[cnt];
        for (int i = 2, k = 0; i <= n; i++) if (isPrime[i]) primes[k++] = i;
        return primes;
    }

    /**
     * Prime factorization: returns map prime->exponent in O(sqrt(n)).
     */
    public static Map<Long, Integer> factorize(long n) {
        var res = new LinkedHashMap<Long, Integer>();
        if (n < 0) n = -n;
        for (long p = 2; p * p <= n; p += (p == 2 ? 1 : 2)) {
            if (n % p != 0) continue;
            var c = 0;
            while (n % p == 0) {
                n /= p;
                c++;
            }
            res.put(p, c);
        }
        if (n > 1) res.put(n, 1);
        return res;
    }
}
```

---

### R.2 Fast Exponentiation

```java
public class FastPow {

    public static long powMod(long a, long e, long mod) {
        a %= mod;
        var r = 1L;
        while (e > 0) {
            if ((e & 1L) == 1L) r = (r * a) % mod;
            a = (a * a) % mod;
            e >>= 1;
        }
        return r;
    }

    /**
     * Fast exponentiation for matrices (square) in O(n^3 log e).
     */
    public static long[][] matPow(long[][] base, long e, long mod) {
        var n = base.length;
        var res = new long[n][n];
        for (var i = 0; i < n; i++) res[i][i] = 1;
        var a = base;
        while (e > 0) {
            if ((e & 1L) == 1L) res = matMul(res, a, mod);
            a = matMul(a, a, mod);
            e >>= 1;
        }
        return res;
    }

    private static long[][] matMul(long[][] x, long[][] y, long mod) {
        var n = x.length;
        var z = new long[n][n];
        for (var i = 0; i < n; i++) {
            for (var k = 0; k < n; k++) {
                if (x[i][k] == 0) continue;
                var xik = x[i][k];
                for (var j = 0; j < n; j++) {
                    z[i][j] = (z[i][j] + xik * y[k][j]) % mod;
                }
            }
        }
        return z;
    }
}
```

---

### R.3 Miller-Rabin Primality (64-bit)

```java
import java.math.BigInteger;

public class MillerRabin64 {

    // Deterministic bases for 64-bit unsigned range.
    // Reference set: {2, 325, 9375, 28178, 450775, 9780504, 1795265022}
    static final long[] BASES = {2, 325, 9375, 28178, 450775, 9780504, 1795265022};

    public static boolean isPrime(long n) {
        if (n < 2) return false;
        for (var p : new long[]{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {
            if (n == p) return true;
            if (n % p == 0) return false;
        }

        long d = n - 1;
        int s = 0;
        while ((d & 1) == 0) {
            d >>= 1;
            s++;
        }

        for (var a : BASES) {
            if (a % n == 0) continue;
            if (!check(a, s, d, n)) return false;
        }
        return true;
    }

    private static boolean check(long a, int s, long d, long n) {
        var x = modPow(a, d, n);
        if (x == 1 || x == n - 1) return true;
        for (var r = 1; r < s; r++) {
            x = mulMod(x, x, n);
            if (x == n - 1) return true;
        }
        return false;
    }

    private static long modPow(long a, long e, long mod) {
        long r = 1;
        long x = a % mod;
        while (e > 0) {
            if ((e & 1) == 1) r = mulMod(r, x, mod);
            x = mulMod(x, x, mod);
            e >>= 1;
        }
        return r;
    }

    // Uses BigInteger to avoid overflow; fine for notes/CP usage.
    private static long mulMod(long a, long b, long mod) {
        return BigInteger.valueOf(a).multiply(BigInteger.valueOf(b)).mod(BigInteger.valueOf(mod)).longValue();
    }
}
```

---

### R.4 Chinese Remainder Theorem (CRT)

```java
public class CRT {

    // returns {r, m} for x ≡ r (mod m), or null if inconsistent
    public static long[] crt(long r1, long m1, long r2, long m2) {
        var eg = extGcd(m1, m2);
        var g = eg[0];
        var x = eg[1];
        var y = eg[2];

        var diff = r2 - r1;
        if (diff % g != 0) return null;

        var lcm = m1 / g * m2;
        var k = modNormalize((diff / g) * x, m2 / g);
        var r = modNormalize(r1 + m1 * k, lcm);
        return new long[]{r, lcm};
    }

    private static long[] extGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        var r = extGcd(b, a % b);
        var g = r[0];
        var x = r[2];
        var y = r[1] - (a / b) * r[2];
        return new long[]{g, x, y};
    }

    private static long modNormalize(long x, long mod) {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }
}
```
