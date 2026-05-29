---
tags: [dsa, leetcode, practice]
aliases: ["DSA Questions"]
status: stable
updated: 2026-05-29
---

# LeetCode Questions - Complete Practice Guide

> [!summary] How to Use This Note
> - Pick a topic, solve a small set, then revise the underlying pattern in [[Algorithms]] and [[DataStructures]].
> - Use the checklists in “Study Plans & Roadmaps” to track progress (core Obsidian checkboxes, no plugins).

> [!tip] Quick Links
> - Concepts: [[Algorithms]] | [[DataStructures]]
> - Java implementations: [[JAVA_IMPL/Java_00_Index_and_CheatSheet]]

Organized by topic, from beginner to advanced. Each section covers a data structure or algorithm with curated problems progressing in difficulty.

**Difficulty Legend**: 🟢 Easy | 🟡 Medium | 🔴 Hard

---

## Table of Contents

1. [Arrays](#1-arrays)
2. [Strings](#2-strings)
3. [Two Pointers](#3-two-pointers)
4. [Sliding Window](#4-sliding-window)
5. [Binary Search](#5-binary-search)
6. [Linked Lists](#6-linked-lists)
7. [Stacks](#7-stacks)
8. [Queues and Deques](#8-queues-and-deques)
9. [Hash Maps and Sets](#9-hash-maps-and-sets)
10. [Sorting](#10-sorting)
11. [Binary Trees](#11-binary-trees)
12. [Binary Search Trees](#12-binary-search-trees)
13. [Heaps / Priority Queues](#13-heaps-priority-queues)
14. [Recursion and Backtracking](#14-recursion-and-backtracking)
15. [Greedy](#15-greedy)
16. [Dynamic Programming](#16-dynamic-programming)
17. [Graphs](#17-graphs)
18. [Tries](#18-tries)
19. [Union-Find](#19-union-find)
20. [Segment Trees and BIT](#20-segment-trees-and-bit)
21. [Bit Manipulation](#21-bit-manipulation)
22. [Math and Number Theory](#22-math-and-number-theory)
23. [Intervals](#23-intervals)
24. [Design Problems](#24-design-problems)
25. [Monotonic Stack / Queue](#25-monotonic-stack-queue)
26. [Study Plans and Roadmaps](#26-study-plans-and-roadmaps)

---

## 1. Arrays

### Beginner

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | 🟢 | Hash map |
| 26 | [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | 🟢 | Two pointers |
| 27 | [Remove Element](https://leetcode.com/problems/remove-element/) | 🟢 | In-place modification |
| 35 | [Search Insert Position](https://leetcode.com/problems/search-insert-position/) | 🟢 | Binary search |
| 66 | [Plus One](https://leetcode.com/problems/plus-one/) | 🟢 | Array traversal |
| 88 | [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | 🟢 | Two pointers from end |
| 118 | [Pascal's Triangle](https://leetcode.com/problems/pascals-triangle/) | 🟢 | Simulation |
| 121 | [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | 🟢 | Track min price |
| 136 | [Single Number](https://leetcode.com/problems/single-number/) | 🟢 | XOR |
| 169 | [Majority Element](https://leetcode.com/problems/majority-element/) | 🟢 | Boyer-Moore voting |
| 217 | [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | 🟢 | Hash set |
| 283 | [Move Zeroes](https://leetcode.com/problems/move-zeroes/) | 🟢 | Two pointers |
| 448 | [Find All Numbers Disappeared in Array](https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/) | 🟢 | Index marking |

### Intermediate

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 11 | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | 🟡 | Two pointers |
| 15 | [3Sum](https://leetcode.com/problems/3sum/) | 🟡 | Sort + two pointers |
| 31 | [Next Permutation](https://leetcode.com/problems/next-permutation/) | 🟡 | Array manipulation |
| 36 | [Valid Sudoku](https://leetcode.com/problems/valid-sudoku/) | 🟡 | Hash sets |
| 48 | [Rotate Image](https://leetcode.com/problems/rotate-image/) | 🟡 | Transpose + reverse |
| 53 | [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | 🟡 | Kadane's algorithm |
| 54 | [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) | 🟡 | Simulation |
| 56 | [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | 🟡 | Sort + merge |
| 73 | [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/) | 🟡 | In-place marking |
| 128 | [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | 🟡 | Hash set |
| 189 | [Rotate Array](https://leetcode.com/problems/rotate-array/) | 🟡 | Reverse trick |
| 238 | [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) | 🟡 | Prefix/suffix products |
| 287 | [Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) | 🟡 | Floyd's cycle |
| 560 | [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | 🟡 | Prefix sum + hash map |

### Advanced

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 4 | [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | 🔴 | Binary search |
| 41 | [First Missing Positive](https://leetcode.com/problems/first-missing-positive/) | 🔴 | Cyclic sort |
| 42 | [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | 🔴 | Two pointers / stack |
| 84 | [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | 🔴 | Monotonic stack |
| 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | 🔴 | Monotonic deque |
| 295 | [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | 🔴 | Two heaps |

---

## 2. Strings

### Beginner

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 13 | [Roman to Integer](https://leetcode.com/problems/roman-to-integer/) | 🟢 | Mapping |
| 14 | [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | 🟢 | Vertical scanning |
| 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | 🟢 | Stack |
| 28 | [Find Index of First Occurrence](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | 🟢 | String matching |
| 125 | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | 🟢 | Two pointers |
| 242 | [Valid Anagram](https://leetcode.com/problems/valid-anagram/) | 🟢 | Frequency count |
| 344 | [Reverse String](https://leetcode.com/problems/reverse-string/) | 🟢 | Two pointers |
| 387 | [First Unique Character in String](https://leetcode.com/problems/first-unique-character-in-a-string/) | 🟢 | Hash map |

### Intermediate

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | 🟡 | Sliding window |
| 5 | [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) | 🟡 | Expand around center / DP |
| 22 | [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | 🟡 | Backtracking |
| 49 | [Group Anagrams](https://leetcode.com/problems/group-anagrams/) | 🟡 | Hash map + sorting |
| 71 | [Simplify Path](https://leetcode.com/problems/simplify-path/) | 🟡 | Stack |
| 91 | [Decode Ways](https://leetcode.com/problems/decode-ways/) | 🟡 | DP |
| 151 | [Reverse Words in a String](https://leetcode.com/problems/reverse-words-in-a-string/) | 🟡 | Split + reverse |
| 227 | [Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) | 🟡 | Stack |
| 271 | [Encode and Decode Strings](https://leetcode.com/problems/encode-and-decode-strings/) | 🟡 | Length encoding |
| 438 | [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | 🟡 | Sliding window |
| 647 | [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) | 🟡 | Expand around center |
| 763 | [Partition Labels](https://leetcode.com/problems/partition-labels/) | 🟡 | Greedy + hash map |

### Advanced

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 10 | [Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/) | 🔴 | DP |
| 32 | [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) | 🔴 | Stack / DP |
| 44 | [Wildcard Matching](https://leetcode.com/problems/wildcard-matching/) | 🔴 | DP |
| 72 | [Edit Distance](https://leetcode.com/problems/edit-distance/) | 🟡 | DP (LCS family) |
| 76 | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | 🔴 | Sliding window |
| 115 | [Distinct Subsequences](https://leetcode.com/problems/distinct-subsequences/) | 🔴 | DP |
| 224 | [Basic Calculator](https://leetcode.com/problems/basic-calculator/) | 🔴 | Stack + recursion |
| 1143 | [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | 🟡 | DP |

---

## 3. Two Pointers

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 125 | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | 🟢 | Opposite direction |
| 167 | [Two Sum II - Sorted Array](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | 🟡 | Opposite direction |
| 15 | [3Sum](https://leetcode.com/problems/3sum/) | 🟡 | Fix one + two pointers |
| 16 | [3Sum Closest](https://leetcode.com/problems/3sum-closest/) | 🟡 | Fix one + two pointers |
| 18 | [4Sum](https://leetcode.com/problems/4sum/) | 🟡 | Fix two + two pointers |
| 11 | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | 🟡 | Opposite direction |
| 75 | [Sort Colors](https://leetcode.com/problems/sort-colors/) | 🟡 | Dutch National Flag |
| 80 | [Remove Duplicates II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) | 🟡 | Read/write pointers |
| 42 | [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | 🔴 | Two pointers |
| 977 | [Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) | 🟢 | Opposite direction |

---

## 4. Sliding Window

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 643 | [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | 🟢 | Fixed window |
| 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | 🟡 | Variable window |
| 424 | [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) | 🟡 | Variable window |
| 567 | [Permutation in String](https://leetcode.com/problems/permutation-in-string/) | 🟡 | Fixed window + freq |
| 438 | [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | 🟡 | Fixed window + freq |
| 209 | [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) | 🟡 | Variable window |
| 904 | [Fruit Into Baskets](https://leetcode.com/problems/fruit-into-baskets/) | 🟡 | Variable window (k=2) |
| 1004 | [Max Consecutive Ones III](https://leetcode.com/problems/max-consecutive-ones-iii/) | 🟡 | Variable window |
| 76 | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | 🔴 | Variable window |
| 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | 🔴 | Monotonic deque |
| 992 | [Subarrays with K Different Integers](https://leetcode.com/problems/subarrays-with-k-different-integers/) | 🔴 | atMost(k) - atMost(k-1) |

---

## 5. Binary Search

### Standard Binary Search

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 704 | [Binary Search](https://leetcode.com/problems/binary-search/) | 🟢 | Basic template |
| 35 | [Search Insert Position](https://leetcode.com/problems/search-insert-position/) | 🟢 | Lower bound |
| 34 | [Find First and Last Position](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | 🟡 | Lower/upper bound |
| 74 | [Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/) | 🟡 | Treat as 1D |
| 240 | [Search a 2D Matrix II](https://leetcode.com/problems/search-a-2d-matrix-ii/) | 🟡 | Staircase search |
| 153 | [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | 🟡 | Modified BS |
| 33 | [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | 🟡 | Modified BS |
| 81 | [Search in Rotated Sorted Array II](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/) | 🟡 | Handle duplicates |
| 162 | [Find Peak Element](https://leetcode.com/problems/find-peak-element/) | 🟡 | Compare neighbors |

### Binary Search on Answer

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 875 | [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | 🟡 | BS on speed |
| 1011 | [Capacity to Ship Packages](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) | 🟡 | BS on capacity |
| 410 | [Split Array Largest Sum](https://leetcode.com/problems/split-array-largest-sum/) | 🔴 | BS on answer |
| 774 | [Minimize Max Distance to Gas Station](https://leetcode.com/problems/minimize-max-distance-to-gas-station/) | 🔴 | BS on answer (float) |
| 4 | [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | 🔴 | BS on partition |
| 668 | [Kth Smallest Number in Multiplication Table](https://leetcode.com/problems/kth-smallest-number-in-multiplication-table/) | 🔴 | BS on value |

---

## 6. Linked Lists

### Beginner

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 206 | [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | 🟢 | Iterative / recursive |
| 21 | [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | 🟢 | Dummy head |
| 141 | [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | 🟢 | Fast/slow pointers |
| 83 | [Remove Duplicates from Sorted List](https://leetcode.com/problems/remove-duplicates-from-sorted-list/) | 🟢 | Pointer manipulation |
| 234 | [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | 🟢 | Reverse half + compare |
| 160 | [Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/) | 🟢 | Two pointers |
| 876 | [Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/) | 🟢 | Fast/slow pointers |

### Intermediate

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 2 | [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | 🟡 | Carry propagation |
| 19 | [Remove Nth Node From End](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | 🟡 | Two pointers with gap |
| 24 | [Swap Nodes in Pairs](https://leetcode.com/problems/swap-nodes-in-pairs/) | 🟡 | Pairwise reversal |
| 61 | [Rotate List](https://leetcode.com/problems/rotate-list/) | 🟡 | Find length + connect |
| 92 | [Reverse Linked List II](https://leetcode.com/problems/reverse-linked-list-ii/) | 🟡 | Reverse sublist |
| 142 | [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) | 🟡 | Floyd's algo |
| 143 | [Reorder List](https://leetcode.com/problems/reorder-list/) | 🟡 | Split + reverse + merge |
| 148 | [Sort List](https://leetcode.com/problems/sort-list/) | 🟡 | Merge sort |
| 138 | [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) | 🟡 | Hash map or interleave |
| 328 | [Odd Even Linked List](https://leetcode.com/problems/odd-even-linked-list/) | 🟡 | Two lists merge |

### Advanced

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 23 | [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | 🔴 | Min-heap / divide & conquer |
| 25 | [Reverse Nodes in K-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/) | 🔴 | K-group reversal |
| 146 | [LRU Cache](https://leetcode.com/problems/lru-cache/) | 🟡 | Doubly LL + Hash map |

---

## 7. Stacks

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | 🟢 | Matching brackets |
| 155 | [Min Stack](https://leetcode.com/problems/min-stack/) | 🟡 | Auxiliary stack |
| 150 | [Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | 🟡 | Stack evaluation |
| 71 | [Simplify Path](https://leetcode.com/problems/simplify-path/) | 🟡 | Stack + split |
| 394 | [Decode String](https://leetcode.com/problems/decode-string/) | 🟡 | Nested stack |
| 735 | [Asteroid Collision](https://leetcode.com/problems/asteroid-collision/) | 🟡 | Stack simulation |
| 739 | [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | 🟡 | Monotonic stack |
| 853 | [Car Fleet](https://leetcode.com/problems/car-fleet/) | 🟡 | Sort + stack |
| 84 | [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | 🔴 | Monotonic stack |
| 85 | [Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) | 🔴 | Histogram per row |
| 224 | [Basic Calculator](https://leetcode.com/problems/basic-calculator/) | 🔴 | Stack + recursion |
| 316 | [Remove Duplicate Letters](https://leetcode.com/problems/remove-duplicate-letters/) | 🟡 | Monotonic stack + greedy |

---

## 8. Queues and Deques

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 225 | [Implement Stack using Queues](https://leetcode.com/problems/implement-stack-using-queues/) | 🟢 | Queue manipulation |
| 232 | [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | 🟢 | Amortized O(1) |
| 346 | [Moving Average from Data Stream](https://leetcode.com/problems/moving-average-from-data-stream/) | 🟢 | Sliding window queue |
| 933 | [Number of Recent Calls](https://leetcode.com/problems/number-of-recent-calls/) | 🟢 | Queue |
| 622 | [Design Circular Queue](https://leetcode.com/problems/design-circular-queue/) | 🟡 | Circular array |
| 641 | [Design Circular Deque](https://leetcode.com/problems/design-circular-deque/) | 🟡 | Circular array |
| 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | 🔴 | Monotonic deque |

---

## 9. Hash Maps and Sets

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | 🟢 | Complement lookup |
| 217 | [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | 🟢 | Hash set |
| 242 | [Valid Anagram](https://leetcode.com/problems/valid-anagram/) | 🟢 | Frequency count |
| 349 | [Intersection of Two Arrays](https://leetcode.com/problems/intersection-of-two-arrays/) | 🟢 | Hash set |
| 383 | [Ransom Note](https://leetcode.com/problems/ransom-note/) | 🟢 | Frequency count |
| 205 | [Isomorphic Strings](https://leetcode.com/problems/isomorphic-strings/) | 🟢 | Two hash maps |
| 290 | [Word Pattern](https://leetcode.com/problems/word-pattern/) | 🟢 | Bijection check |
| 49 | [Group Anagrams](https://leetcode.com/problems/group-anagrams/) | 🟡 | Sorted key |
| 128 | [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | 🟡 | Hash set + sequence start |
| 347 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | 🟡 | Hash map + bucket sort |
| 380 | [Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) | 🟡 | Hash map + array |
| 560 | [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | 🟡 | Prefix sum + hash map |
| 706 | [Design HashMap](https://leetcode.com/problems/design-hashmap/) | 🟢 | Chaining / open addressing |

---

## 10. Sorting

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 912 | [Sort an Array](https://leetcode.com/problems/sort-an-array/) | 🟡 | Merge/Quick/Heap sort |
| 75 | [Sort Colors](https://leetcode.com/problems/sort-colors/) | 🟡 | Dutch National Flag |
| 148 | [Sort List](https://leetcode.com/problems/sort-list/) | 🟡 | Merge sort on linked list |
| 179 | [Largest Number](https://leetcode.com/problems/largest-number/) | 🟡 | Custom comparator |
| 215 | [Kth Largest Element](https://leetcode.com/problems/kth-largest-element-in-an-array/) | 🟡 | Quick select |
| 324 | [Wiggle Sort II](https://leetcode.com/problems/wiggle-sort-ii/) | 🟡 | Median + 3-way partition |
| 315 | [Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | 🔴 | Merge sort / BIT |
| 493 | [Reverse Pairs](https://leetcode.com/problems/reverse-pairs/) | 🔴 | Merge sort |
| 164 | [Maximum Gap](https://leetcode.com/problems/maximum-gap/) | 🟡 | Bucket sort / radix sort |

---

## 11. Binary Trees

### Traversal & Basic

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 94 | [Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/) | 🟢 | Recursive / iterative |
| 144 | [Binary Tree Preorder Traversal](https://leetcode.com/problems/binary-tree-preorder-traversal/) | 🟢 | Stack |
| 145 | [Binary Tree Postorder Traversal](https://leetcode.com/problems/binary-tree-postorder-traversal/) | 🟢 | Two stacks |
| 102 | [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) | 🟡 | BFS |
| 104 | [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | 🟢 | DFS |
| 111 | [Minimum Depth of Binary Tree](https://leetcode.com/problems/minimum-depth-of-binary-tree/) | 🟢 | BFS / DFS |
| 226 | [Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) | 🟢 | DFS |
| 100 | [Same Tree](https://leetcode.com/problems/same-tree/) | 🟢 | DFS comparison |
| 101 | [Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) | 🟢 | Mirror check |
| 572 | [Subtree of Another Tree](https://leetcode.com/problems/subtree-of-another-tree/) | 🟢 | DFS + match |

### Intermediate

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 105 | [Construct Binary Tree from Preorder and Inorder](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) | 🟡 | Divide & conquer |
| 106 | [Construct Binary Tree from Inorder and Postorder](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/) | 🟡 | Divide & conquer |
| 110 | [Balanced Binary Tree](https://leetcode.com/problems/balanced-binary-tree/) | 🟢 | Height check |
| 112 | [Path Sum](https://leetcode.com/problems/path-sum/) | 🟢 | DFS |
| 113 | [Path Sum II](https://leetcode.com/problems/path-sum-ii/) | 🟡 | DFS + backtracking |
| 114 | [Flatten Binary Tree to Linked List](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/) | 🟡 | Morris-like |
| 199 | [Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/) | 🟡 | BFS (last of level) |
| 236 | [Lowest Common Ancestor](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | 🟡 | DFS |
| 543 | [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | 🟢 | DFS + track max |
| 863 | [All Nodes Distance K in Binary Tree](https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/) | 🟡 | Parent map + BFS |
| 987 | [Vertical Order Traversal](https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/) | 🔴 | BFS + sorting |

### Advanced

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 124 | [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | 🔴 | DFS + track max |
| 297 | [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) | 🔴 | BFS / DFS |
| 968 | [Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/) | 🔴 | Greedy DFS |

---

## 12. Binary Search Trees

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 700 | [Search in a BST](https://leetcode.com/problems/search-in-a-binary-search-tree/) | 🟢 | BST property |
| 701 | [Insert into a BST](https://leetcode.com/problems/insert-into-a-binary-search-tree/) | 🟡 | BST insert |
| 450 | [Delete Node in a BST](https://leetcode.com/problems/delete-node-in-a-bst/) | 🟡 | Three cases |
| 98 | [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) | 🟡 | Range check / inorder |
| 230 | [Kth Smallest Element in BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) | 🟡 | Inorder traversal |
| 235 | [LCA of a BST](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | 🟡 | BST property |
| 108 | [Convert Sorted Array to BST](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/) | 🟢 | Binary divide |
| 173 | [BST Iterator](https://leetcode.com/problems/binary-search-tree-iterator/) | 🟡 | Controlled inorder |
| 96 | [Unique Binary Search Trees](https://leetcode.com/problems/unique-binary-search-trees/) | 🟡 | Catalan numbers / DP |
| 95 | [Unique Binary Search Trees II](https://leetcode.com/problems/unique-binary-search-trees-ii/) | 🟡 | Recursive generation |

---

## 13. Heaps / Priority Queues

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 703 | [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | 🟢 | Min-heap of size k |
| 1046 | [Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) | 🟢 | Max-heap |
| 215 | [Kth Largest Element in Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | 🟡 | Quick select / heap |
| 347 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | 🟡 | Min-heap / bucket sort |
| 373 | [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) | 🟡 | Min-heap |
| 621 | [Task Scheduler](https://leetcode.com/problems/task-scheduler/) | 🟡 | Max-heap + cooldown |
| 973 | [K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) | 🟡 | Max-heap of size k |
| 355 | [Design Twitter](https://leetcode.com/problems/design-twitter/) | 🟡 | Merge k sorted + heap |
| 23 | [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | 🔴 | Min-heap |
| 295 | [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | 🔴 | Two heaps |
| 480 | [Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) | 🔴 | Two heaps + lazy removal |
| 502 | [IPO](https://leetcode.com/problems/ipo/) | 🔴 | Two heaps (greedy) |

---

## 14. Recursion and Backtracking

### Recursion Basics

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 509 | [Fibonacci Number](https://leetcode.com/problems/fibonacci-number/) | 🟢 | Basic recursion / DP |
| 50 | [Pow(x, n)](https://leetcode.com/problems/powx-n/) | 🟡 | Fast exponentiation |
| 779 | [K-th Symbol in Grammar](https://leetcode.com/problems/k-th-symbol-in-grammar/) | 🟡 | Recursive pattern |

### Backtracking

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 46 | [Permutations](https://leetcode.com/problems/permutations/) | 🟡 | Swap / visited array |
| 47 | [Permutations II](https://leetcode.com/problems/permutations-ii/) | 🟡 | Skip duplicates |
| 78 | [Subsets](https://leetcode.com/problems/subsets/) | 🟡 | Include/exclude |
| 90 | [Subsets II](https://leetcode.com/problems/subsets-ii/) | 🟡 | Sort + skip duplicates |
| 39 | [Combination Sum](https://leetcode.com/problems/combination-sum/) | 🟡 | Unbounded choices |
| 40 | [Combination Sum II](https://leetcode.com/problems/combination-sum-ii/) | 🟡 | Each element once |
| 77 | [Combinations](https://leetcode.com/problems/combinations/) | 🟡 | Choose k from n |
| 22 | [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | 🟡 | Valid parentheses |
| 17 | [Letter Combinations of Phone Number](https://leetcode.com/problems/letter-combinations-of-a-phone-number/) | 🟡 | Character mapping |
| 79 | [Word Search](https://leetcode.com/problems/word-search/) | 🟡 | Grid DFS |
| 131 | [Palindrome Partitioning](https://leetcode.com/problems/palindrome-partitioning/) | 🟡 | Partition + check |
| 51 | [N-Queens](https://leetcode.com/problems/n-queens/) | 🔴 | Column/diagonal check |
| 52 | [N-Queens II](https://leetcode.com/problems/n-queens-ii/) | 🔴 | Count solutions |
| 37 | [Sudoku Solver](https://leetcode.com/problems/sudoku-solver/) | 🔴 | Constraint backtracking |
| 212 | [Word Search II](https://leetcode.com/problems/word-search-ii/) | 🔴 | Trie + backtracking |
| 980 | [Unique Paths III](https://leetcode.com/problems/unique-paths-iii/) | 🔴 | Hamiltonian path |

---

## 15. Greedy

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 455 | [Assign Cookies](https://leetcode.com/problems/assign-cookies/) | 🟢 | Sort + two pointers |
| 860 | [Lemonade Change](https://leetcode.com/problems/lemonade-change/) | 🟢 | Greedy change |
| 55 | [Jump Game](https://leetcode.com/problems/jump-game/) | 🟡 | Track max reach |
| 45 | [Jump Game II](https://leetcode.com/problems/jump-game-ii/) | 🟡 | BFS / greedy |
| 134 | [Gas Station](https://leetcode.com/problems/gas-station/) | 🟡 | Circular greedy |
| 135 | [Candy](https://leetcode.com/problems/candy/) | 🔴 | Two pass |
| 376 | [Wiggle Subsequence](https://leetcode.com/problems/wiggle-subsequence/) | 🟡 | Track direction changes |
| 435 | [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | 🟡 | Sort by end |
| 452 | [Minimum Number of Arrows](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) | 🟡 | Sort by end |
| 621 | [Task Scheduler](https://leetcode.com/problems/task-scheduler/) | 🟡 | Math / heap |
| 763 | [Partition Labels](https://leetcode.com/problems/partition-labels/) | 🟡 | Last occurrence |
| 846 | [Hand of Straights](https://leetcode.com/problems/hand-of-straights/) | 🟡 | Sorted map |
| 1899 | [Merge Triplets to Form Target Triplet](https://leetcode.com/problems/merge-triplets-to-form-target-triplet/) | 🟡 | Filter + check |
| 678 | [Valid Parenthesis String](https://leetcode.com/problems/valid-parenthesis-string/) | 🟡 | Range tracking |

---

## 16. Dynamic Programming

### 1D DP

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 70 | [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | 🟢 | Fibonacci |
| 198 | [House Robber](https://leetcode.com/problems/house-robber/) | 🟡 | Rob or skip |
| 213 | [House Robber II](https://leetcode.com/problems/house-robber-ii/) | 🟡 | Circular |
| 746 | [Min Cost Climbing Stairs](https://leetcode.com/problems/min-cost-climbing-stairs/) | 🟢 | Min path |
| 139 | [Word Break](https://leetcode.com/problems/word-break/) | 🟡 | String DP |
| 300 | [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | 🟡 | LIS (O(n log n)) |
| 322 | [Coin Change](https://leetcode.com/problems/coin-change/) | 🟡 | Unbounded knapsack |
| 518 | [Coin Change II](https://leetcode.com/problems/coin-change-ii/) | 🟡 | Count ways |
| 152 | [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) | 🟡 | Track min and max |
| 91 | [Decode Ways](https://leetcode.com/problems/decode-ways/) | 🟡 | String partition |

### 2D DP

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 62 | [Unique Paths](https://leetcode.com/problems/unique-paths/) | 🟡 | Grid DP |
| 63 | [Unique Paths II](https://leetcode.com/problems/unique-paths-ii/) | 🟡 | Grid + obstacles |
| 64 | [Minimum Path Sum](https://leetcode.com/problems/minimum-path-sum/) | 🟡 | Grid DP |
| 120 | [Triangle](https://leetcode.com/problems/triangle/) | 🟡 | Bottom-up |
| 221 | [Maximal Square](https://leetcode.com/problems/maximal-square/) | 🟡 | Min of 3 neighbors + 1 |
| 85 | [Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) | 🔴 | Histogram per row |

### Knapsack Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 416 | [Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/) | 🟡 | 0/1 knapsack |
| 494 | [Target Sum](https://leetcode.com/problems/target-sum/) | 🟡 | Count subset sum |
| 474 | [Ones and Zeroes](https://leetcode.com/problems/ones-and-zeroes/) | 🟡 | 2D knapsack |
| 1049 | [Last Stone Weight II](https://leetcode.com/problems/last-stone-weight-ii/) | 🟡 | Min subset diff |

### String DP (LCS Family)

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 1143 | [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | 🟡 | LCS |
| 72 | [Edit Distance](https://leetcode.com/problems/edit-distance/) | 🟡 | Insert/delete/replace |
| 115 | [Distinct Subsequences](https://leetcode.com/problems/distinct-subsequences/) | 🔴 | Count subsequences |
| 583 | [Delete Operation for Two Strings](https://leetcode.com/problems/delete-operation-for-two-strings/) | 🟡 | LCS variant |
| 97 | [Interleaving String](https://leetcode.com/problems/interleaving-string/) | 🟡 | 2D DP |
| 1312 | [Min Insertions for Palindrome](https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/) | 🔴 | LPS variant |
| 516 | [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/) | 🟡 | Reverse + LCS |

### Interval DP

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 312 | [Burst Balloons](https://leetcode.com/problems/burst-balloons/) | 🔴 | Interval DP |
| 1039 | [Minimum Score Triangulation](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/) | 🟡 | MCM variant |
| 132 | [Palindrome Partitioning II](https://leetcode.com/problems/palindrome-partitioning-ii/) | 🔴 | Min cuts |
| 87 | [Scramble String](https://leetcode.com/problems/scramble-string/) | 🔴 | Interval DP + memo |

### Stock Trading (State Machine DP)

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 121 | [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | 🟢 | One transaction |
| 122 | [Best Time to Buy and Sell Stock II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | 🟡 | Unlimited transactions |
| 123 | [Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) | 🔴 | At most 2 transactions |
| 188 | [Best Time to Buy and Sell Stock IV](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) | 🔴 | At most k transactions |
| 309 | [Best Time with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) | 🟡 | State machine |
| 714 | [Best Time with Transaction Fee](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) | 🟡 | State machine |

### Advanced DP

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 10 | [Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/) | 🔴 | String DP |
| 44 | [Wildcard Matching](https://leetcode.com/problems/wildcard-matching/) | 🔴 | String DP |
| 174 | [Dungeon Game](https://leetcode.com/problems/dungeon-game/) | 🔴 | Reverse grid DP |
| 329 | [Longest Increasing Path in a Matrix](https://leetcode.com/problems/longest-increasing-path-in-a-matrix/) | 🔴 | DFS + memo |
| 354 | [Russian Doll Envelopes](https://leetcode.com/problems/russian-doll-envelopes/) | 🔴 | Sort + LIS |
| 403 | [Frog Jump](https://leetcode.com/problems/frog-jump/) | 🔴 | State: (stone, jump) |
| 1000 | [Minimum Cost to Merge Stones](https://leetcode.com/problems/minimum-cost-to-merge-stones/) | 🔴 | Interval DP |

### Bitmask DP

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 464 | [Can I Win](https://leetcode.com/problems/can-i-win/) | 🟡 | Game theory + bitmask |
| 473 | [Matchsticks to Square](https://leetcode.com/problems/matchsticks-to-square/) | 🟡 | Partition + bitmask |
| 698 | [Partition to K Equal Sum Subsets](https://leetcode.com/problems/partition-to-k-equal-sum-subsets/) | 🟡 | Bitmask DP |
| 691 | [Stickers to Spell Word](https://leetcode.com/problems/stickers-to-spell-word/) | 🔴 | Bitmask DP |
| 943 | [Find the Shortest Superstring](https://leetcode.com/problems/find-the-shortest-superstring/) | 🔴 | TSP variant |
| 1125 | [Smallest Sufficient Team](https://leetcode.com/problems/smallest-sufficient-team/) | 🔴 | Set cover + bitmask |

### DP on Trees

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 337 | [House Robber III](https://leetcode.com/problems/house-robber-iii/) | 🟡 | Rob/skip on tree |
| 124 | [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | 🔴 | DFS + track max |
| 968 | [Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/) | 🔴 | 3-state DP |

---

## 17. Graphs

### BFS / DFS Basics

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 200 | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | 🟡 | DFS/BFS flood fill |
| 733 | [Flood Fill](https://leetcode.com/problems/flood-fill/) | 🟢 | DFS/BFS |
| 695 | [Max Area of Island](https://leetcode.com/problems/max-area-of-island/) | 🟡 | DFS |
| 994 | [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | 🟡 | Multi-source BFS |
| 542 | [01 Matrix](https://leetcode.com/problems/01-matrix/) | 🟡 | Multi-source BFS |
| 130 | [Surrounded Regions](https://leetcode.com/problems/surrounded-regions/) | 🟡 | Border DFS |
| 417 | [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) | 🟡 | Two BFS from oceans |
| 133 | [Clone Graph](https://leetcode.com/problems/clone-graph/) | 🟡 | DFS/BFS + hash map |
| 841 | [Keys and Rooms](https://leetcode.com/problems/keys-and-rooms/) | 🟡 | DFS |
| 1091 | [Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | 🟡 | BFS |
| 286 | [Walls and Gates](https://leetcode.com/problems/walls-and-gates/) | 🟡 | Multi-source BFS |

### Topological Sort

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 207 | [Course Schedule](https://leetcode.com/problems/course-schedule/) | 🟡 | Cycle detection |
| 210 | [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) | 🟡 | Topological order |
| 269 | [Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) | 🔴 | Build graph + topo sort |
| 802 | [Find Eventual Safe States](https://leetcode.com/problems/find-eventual-safe-states/) | 🟡 | Reverse graph + topo |
| 1203 | [Sort Items by Groups](https://leetcode.com/problems/sort-items-by-groups-respecting-dependencies/) | 🔴 | Two-level topo sort |

### Shortest Path

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 743 | [Network Delay Time](https://leetcode.com/problems/network-delay-time/) | 🟡 | Dijkstra's |
| 787 | [Cheapest Flights Within K Stops](https://leetcode.com/problems/cheapest-flights-within-k-stops/) | 🟡 | Bellman-Ford / BFS |
| 1514 | [Path with Maximum Probability](https://leetcode.com/problems/path-with-maximum-probability/) | 🟡 | Modified Dijkstra |
| 778 | [Swim in Rising Water](https://leetcode.com/problems/swim-in-rising-water/) | 🔴 | Dijkstra / BS + BFS |
| 1631 | [Path With Minimum Effort](https://leetcode.com/problems/path-with-minimum-effort/) | 🟡 | Dijkstra / BS + BFS |
| 505 | [The Maze II](https://leetcode.com/problems/the-maze-ii/) | 🟡 | Dijkstra |
| 882 | [Reachable Nodes in Subdivided Graph](https://leetcode.com/problems/reachable-nodes-in-subdivided-graph/) | 🔴 | Dijkstra |

### MST

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 1135 | [Connecting Cities With Minimum Cost](https://leetcode.com/problems/connecting-cities-with-minimum-cost/) | 🟡 | Kruskal's / Prim's |
| 1584 | [Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/) | 🟡 | Prim's / Kruskal's |
| 1489 | [Find Critical and Pseudo-Critical Edges](https://leetcode.com/problems/find-critical-and-pseudo-critical-edges-in-mst/) | 🔴 | MST + edge analysis |

### Advanced Graph

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 127 | [Word Ladder](https://leetcode.com/problems/word-ladder/) | 🔴 | BFS |
| 126 | [Word Ladder II](https://leetcode.com/problems/word-ladder-ii/) | 🔴 | BFS + backtracking |
| 332 | [Reconstruct Itinerary](https://leetcode.com/problems/reconstruct-itinerary/) | 🔴 | Euler path (Hierholzer's) |
| 685 | [Redundant Connection II](https://leetcode.com/problems/redundant-connection-ii/) | 🔴 | Directed graph + UF |
| 1192 | [Critical Connections](https://leetcode.com/problems/critical-connections-in-a-network/) | 🔴 | Tarjan's bridges |
| 399 | [Evaluate Division](https://leetcode.com/problems/evaluate-division/) | 🟡 | Weighted graph DFS |
| 785 | [Is Graph Bipartite](https://leetcode.com/problems/is-graph-bipartite/) | 🟡 | 2-coloring |
| 1043 | [Partition Array for Maximum Sum](https://leetcode.com/problems/partition-array-for-maximum-sum/) | 🟡 | DP |

---

## 18. Tries

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 208 | [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | 🟡 | Basic trie ops |
| 211 | [Design Add and Search Words](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | 🟡 | Trie + DFS (wildcard) |
| 14 | [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | 🟢 | Trie or vertical scan |
| 648 | [Replace Words](https://leetcode.com/problems/replace-words/) | 🟡 | Trie prefix lookup |
| 677 | [Map Sum Pairs](https://leetcode.com/problems/map-sum-pairs/) | 🟡 | Trie with values |
| 212 | [Word Search II](https://leetcode.com/problems/word-search-ii/) | 🔴 | Trie + backtracking |
| 421 | [Maximum XOR of Two Numbers](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/) | 🟡 | Bitwise trie |
| 472 | [Concatenated Words](https://leetcode.com/problems/concatenated-words/) | 🔴 | Trie + DFS |
| 745 | [Prefix and Suffix Search](https://leetcode.com/problems/prefix-and-suffix-search/) | 🔴 | Trie design |
| 1268 | [Search Suggestions System](https://leetcode.com/problems/search-suggestions-system/) | 🟡 | Trie + DFS / BS |

---

## 19. Union-Find

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 684 | [Redundant Connection](https://leetcode.com/problems/redundant-connection/) | 🟡 | Detect cycle |
| 200 | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | 🟡 | UF approach |
| 547 | [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | 🟡 | Connected components |
| 721 | [Accounts Merge](https://leetcode.com/problems/accounts-merge/) | 🟡 | UF + hash map |
| 128 | [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | 🟡 | UF / hash set |
| 305 | [Number of Islands II](https://leetcode.com/problems/number-of-islands-ii/) | 🔴 | Dynamic UF |
| 765 | [Couples Holding Hands](https://leetcode.com/problems/couples-holding-hands/) | 🔴 | UF / greedy |
| 839 | [Similar String Groups](https://leetcode.com/problems/similar-string-groups/) | 🔴 | UF + pairwise check |
| 952 | [Largest Component Size by Common Factor](https://leetcode.com/problems/largest-component-size-by-common-factor/) | 🔴 | UF + factorization |
| 1202 | [Smallest String With Swaps](https://leetcode.com/problems/smallest-string-with-swaps/) | 🟡 | UF + sort components |
| 1584 | [Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/) | 🟡 | Kruskal's + UF |

---

## 20. Segment Trees and BIT

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 307 | [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | 🟡 | BIT / Segment Tree |
| 303 | [Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | 🟢 | Prefix sum |
| 304 | [Range Sum Query 2D - Immutable](https://leetcode.com/problems/range-sum-query-2d-immutable/) | 🟡 | 2D prefix sum |
| 315 | [Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | 🔴 | BIT / merge sort |
| 493 | [Reverse Pairs](https://leetcode.com/problems/reverse-pairs/) | 🔴 | BIT / merge sort |
| 327 | [Count of Range Sum](https://leetcode.com/problems/count-of-range-sum/) | 🔴 | Merge sort / BIT |
| 699 | [Falling Squares](https://leetcode.com/problems/falling-squares/) | 🔴 | Segment tree / coordinate compression |
| 218 | [The Skyline Problem](https://leetcode.com/problems/the-skyline-problem/) | 🔴 | Sweep line + heap/seg tree |
| 1157 | [Online Majority Element In Subarray](https://leetcode.com/problems/online-majority-element-in-subarray/) | 🔴 | Segment tree + random |

---

## 21. Bit Manipulation

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 136 | [Single Number](https://leetcode.com/problems/single-number/) | 🟢 | XOR |
| 137 | [Single Number II](https://leetcode.com/problems/single-number-ii/) | 🟡 | Bit counting mod 3 |
| 260 | [Single Number III](https://leetcode.com/problems/single-number-iii/) | 🟡 | XOR + partition |
| 191 | [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/) | 🟢 | Brian Kernighan's |
| 190 | [Reverse Bits](https://leetcode.com/problems/reverse-bits/) | 🟢 | Bit by bit |
| 268 | [Missing Number](https://leetcode.com/problems/missing-number/) | 🟢 | XOR or math |
| 338 | [Counting Bits](https://leetcode.com/problems/counting-bits/) | 🟢 | DP on bits |
| 371 | [Sum of Two Integers](https://leetcode.com/problems/sum-of-two-integers/) | 🟡 | Bit addition |
| 201 | [Bitwise AND of Numbers Range](https://leetcode.com/problems/bitwise-and-of-numbers-range/) | 🟡 | Common prefix |
| 78 | [Subsets](https://leetcode.com/problems/subsets/) | 🟡 | Bitmask enumeration |
| 461 | [Hamming Distance](https://leetcode.com/problems/hamming-distance/) | 🟢 | XOR + popcount |
| 29 | [Divide Two Integers](https://leetcode.com/problems/divide-two-integers/) | 🟡 | Bit shifting |

---

## 22. Math and Number Theory

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 7 | [Reverse Integer](https://leetcode.com/problems/reverse-integer/) | 🟡 | Overflow check |
| 9 | [Palindrome Number](https://leetcode.com/problems/palindrome-number/) | 🟢 | Reverse half |
| 12 | [Integer to Roman](https://leetcode.com/problems/integer-to-roman/) | 🟡 | Greedy mapping |
| 50 | [Pow(x, n)](https://leetcode.com/problems/powx-n/) | 🟡 | Fast exponentiation |
| 69 | [Sqrt(x)](https://leetcode.com/problems/sqrtx/) | 🟢 | Binary search |
| 149 | [Max Points on a Line](https://leetcode.com/problems/max-points-on-a-line/) | 🔴 | GCD for slope |
| 168 | [Excel Sheet Column Title](https://leetcode.com/problems/excel-sheet-column-title/) | 🟢 | Base conversion |
| 172 | [Factorial Trailing Zeroes](https://leetcode.com/problems/factorial-trailing-zeroes/) | 🟡 | Count factor 5 |
| 202 | [Happy Number](https://leetcode.com/problems/happy-number/) | 🟢 | Floyd's cycle |
| 204 | [Count Primes](https://leetcode.com/problems/count-primes/) | 🟡 | Sieve of Eratosthenes |
| 279 | [Perfect Squares](https://leetcode.com/problems/perfect-squares/) | 🟡 | DP / BFS |
| 343 | [Integer Break](https://leetcode.com/problems/integer-break/) | 🟡 | Math / DP |
| 365 | [Water and Jug Problem](https://leetcode.com/problems/water-and-jug-problem/) | 🟡 | GCD (Bezout's) |
| 372 | [Super Pow](https://leetcode.com/problems/super-pow/) | 🟡 | Modular exponent |
| 1979 | [Find GCD of Array](https://leetcode.com/problems/find-greatest-common-divisor-of-array/) | 🟢 | GCD |
| 2013 | [Detect Squares](https://leetcode.com/problems/detect-squares/) | 🟡 | Hash map geometry |

---

## 23. Intervals

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 56 | [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | 🟡 | Sort + merge |
| 57 | [Insert Interval](https://leetcode.com/problems/insert-interval/) | 🟡 | Binary search + merge |
| 252 | [Meeting Rooms](https://leetcode.com/problems/meeting-rooms/) | 🟢 | Sort + check overlap |
| 253 | [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | 🟡 | Min-heap / sweep line |
| 435 | [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | 🟡 | Greedy by end |
| 452 | [Minimum Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) | 🟡 | Greedy by end |
| 986 | [Interval List Intersections](https://leetcode.com/problems/interval-list-intersections/) | 🟡 | Two pointers |
| 1288 | [Remove Covered Intervals](https://leetcode.com/problems/remove-covered-intervals/) | 🟡 | Sort + greedy |
| 759 | [Employee Free Time](https://leetcode.com/problems/employee-free-time/) | 🔴 | Merge + gaps |

---

## 24. Design Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 146 | [LRU Cache](https://leetcode.com/problems/lru-cache/) | 🟡 | Doubly LL + HashMap |
| 460 | [LFU Cache](https://leetcode.com/problems/lfu-cache/) | 🔴 | Two HashMaps + DLL per freq |
| 155 | [Min Stack](https://leetcode.com/problems/min-stack/) | 🟡 | Auxiliary stack |
| 208 | [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) | 🟡 | Trie |
| 295 | [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | 🔴 | Two heaps |
| 355 | [Design Twitter](https://leetcode.com/problems/design-twitter/) | 🟡 | OOP + heap |
| 380 | [Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) | 🟡 | Array + HashMap |
| 381 | [Insert Delete GetRandom O(1) Duplicates](https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/) | 🔴 | Array + HashMap + Set |
| 706 | [Design HashMap](https://leetcode.com/problems/design-hashmap/) | 🟢 | Chaining |
| 707 | [Design Linked List](https://leetcode.com/problems/design-linked-list/) | 🟡 | Linked list |
| 1166 | [Design File System](https://leetcode.com/problems/design-file-system/) | 🟡 | Trie / HashMap |
| 1472 | [Design Browser History](https://leetcode.com/problems/design-browser-history/) | 🟡 | Stack / DLL |
| 588 | [Design In-Memory File System](https://leetcode.com/problems/design-in-memory-file-system/) | 🔴 | Trie |

---

## 25. Monotonic Stack / Queue

| # | Problem | Difficulty | Key Concept |
|---|---------|:---:|-------------|
| 496 | [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) | 🟢 | Monotonic stack |
| 503 | [Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) | 🟡 | Circular + monotonic stack |
| 739 | [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | 🟡 | Decreasing stack |
| 84 | [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | 🔴 | Increasing stack |
| 85 | [Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) | 🔴 | Histogram per row |
| 42 | [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | 🔴 | Stack approach |
| 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | 🔴 | Monotonic deque |
| 907 | [Sum of Subarray Minimums](https://leetcode.com/problems/sum-of-subarray-minimums/) | 🟡 | Monotonic stack |
| 316 | [Remove Duplicate Letters](https://leetcode.com/problems/remove-duplicate-letters/) | 🟡 | Monotonic stack + greedy |
| 402 | [Remove K Digits](https://leetcode.com/problems/remove-k-digits/) | 🟡 | Monotonic stack |
| 1856 | [Maximum Subarray Min-Product](https://leetcode.com/problems/maximum-subarray-min-product/) | 🟡 | Monotonic stack + prefix sum |

---

## Tree Queries (Euler Tour, LCA, HLD)

- Structured set (AtCoder-style):
  - Subtree sums via Euler tour + Fenwick/Segment tree
  - Path queries via HLD (sum/min/max on u↔v)
- Fast/tricky boosters (CF-style):
  - Mixed path/subtree operations (require careful decomposition)
- Re-solve checkboxes: [ ] Day 7 [ ] Day 14 [ ] Day 30
- Mistake journal: invariants for base array mapping; off-by-one in tin/tout; chain boundaries

## Offline Queries (Mo’s, sweep line, sort+BIT)

- Structured set: sort+BIT inversions/kth; sweep line rectangles; Mo’s on frequency queries
- Fast/tricky boosters: Mo’s with tricky add/remove cost; boundary ties in sweeps
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: tie-breaking in events; compression errors; Mo’s state not reverted correctly

## 2-SAT

- Structured set: clauses modeling, satisfiability, assignment extraction
- Boosters: edge cases with forced assignments, XOR sets
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: wrong mapping a/¬a; wrong SCC order when assigning

## Min-Cost Max-Flow

- Structured set: min-cost matching/assignment; circulation with demands
- Boosters: negative edges and potentials; path reconstruction correctness
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: reverse edges costs; overflow; not updating potentials

## Suffix Automaton / Advanced Strings

- Structured set: distinct substrings; occurrences; LCS with SAM
- Boosters: combining SAM with DP; counting constrained substrings
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: clone logic in SAM; `len`/`link` off-by-one

## DP Optimizations (D&C, Knuth, CHT)

- Structured set: classic problems that admit optimizations
- Boosters: prove/spot monotone opt / quadrangle inequality
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: applying optimization without proof; wrong transition order

## Convolution (FFT/NTT) (Optional Advanced)

- Structured set: polynomial multiplication tasks; convolution-friendly models
- Boosters: convolution tricks in substring problems
- Re-solve: [ ] D7 [ ] D14 [ ] D30
- Mistakes: rounding (FFT); wrong mod/root selection (NTT)

## 26. Study Plans and Roadmaps

### Recommended Problem-Solving Order

#### Week 1-2: Arrays, Strings, Hash Maps
Start with: #1, #217, #242, #125, #121, #283, #88, #14, #20, #49, #128

#### Week 3-4: Two Pointers, Sliding Window, Binary Search
Start with: #167, #15, #11, #3, #424, #76, #704, #33, #875

#### Week 5-6: Linked Lists, Stacks, Queues
Start with: #206, #21, #141, #19, #143, #155, #739, #84, #23

#### Week 7-8: Trees
Start with: #104, #226, #100, #102, #98, #230, #236, #105, #124, #297

#### Week 9-10: Heaps, Greedy
Start with: #215, #347, #295, #621, #55, #45, #134, #435, #763

#### Week 11-14: Dynamic Programming
Start with: #70, #198, #322, #300, #1143, #72, #416, #62, #121-series, #312

#### Week 15-17: Graphs
Start with: #200, #133, #994, #207, #210, #743, #787, #127, #1192

#### Week 18-20: Advanced Topics
Tries, Union-Find, Segment Trees, Bit Manipulation, Intervals, Design

### Curated Lists

| List | Count | Description |
|------|:---:|-------------|
| [Blind 75](https://leetcode.com/discuss/general-discussion/460599/blind-75-leetcode-questions) | 75 | Essential interview problems |
| [NeetCode 150](https://neetcode.io/practice) | 150 | Extended Blind 75 with categories |
| [NeetCode All](https://neetcode.io/practice) | 300+ | Comprehensive coverage |
| [Grind 75](https://www.techinterviewhandbook.org/grind75) | 75 | Customizable study plan |
| [Striver's SDE Sheet](https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/) | 191 | Covers all major topics |
| [Sean Prashad's Patterns](https://seanprashad.com/leetcode-patterns/) | 170+ | Organized by pattern |
| [LeetCode Top 100 Liked](https://leetcode.com/problem-list/top-100-liked-questions/) | 100 | Community favorites |
| [LeetCode Top Interview](https://leetcode.com/problem-list/top-interview-questions/) | 145 | Frequently asked |

### Tips for Practice

1. **Understand the pattern** — don't just memorize solutions
2. **Time yourself** — aim for 20-30 min for medium, 40-60 min for hard
3. **Solve without hints first** — struggle builds understanding
4. **Review solutions** — learn from optimal approaches
5. **Revisit problems** — re-solve after 1-2 weeks
6. **Write clean code** — variable names, edge cases, comments
7. **Analyze complexity** — always state time and space complexity
8. **Practice explaining** — talk through your approach out loud

### Resources for Problem Solutions

- [NeetCode (YouTube)](https://www.youtube.com/@NeetCode) — excellent video explanations
- [Striver / take U forward (YouTube)](https://www.youtube.com/@takeUforward) — comprehensive DSA
- [Back To Back SWE (YouTube)](https://www.youtube.com/@BackToBackSWE) — in-depth explanations
- [LeetCode Discuss](https://leetcode.com/discuss/) — community solutions
- [CP-Algorithms](https://cp-algorithms.com/) — competitive programming reference
- [GeeksforGeeks](https://www.geeksforgeeks.org/) — tutorials and solutions
