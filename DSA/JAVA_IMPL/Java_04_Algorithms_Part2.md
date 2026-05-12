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

### Section Q: String Algorithms
- [Q.1 KMP Pattern Matching](#q-1-kmp-pattern-matching)
- [Q.2 Rolling Hash](#q-2-rolling-hash)
- [Q.3 Manacher's Algorithm](#q-3-manacher-s-algorithm)

### Section R: Mathematical Algorithms
- [R.1 Number Theory](#r-1-number-theory)
- [R.2 Fast Exponentiation](#r-2-fast-exponentiation)

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

*Continue with remaining sections...*