# Java 06: Advanced Algorithms (Competitive Programming)

CP-focused Java 17+ implementations for advanced algorithms referenced from [[Algorithms]].

---

## Table of Contents

- [Section S: Network Flow](#section-s-network-flow)
- [S.1 Dinic's Max Flow](#s1-dinic-s-max-flow)
- [S.2 Min-Cost Max-Flow](#s2-min-cost-max-flow)
- [Section T: FFT / NTT](#section-t-fft-ntt)
- [T.1 FFT Convolution (Complex)](#t1-fft-convolution-complex)
- [T.2 NTT Convolution (Mod Prime)](#t2-ntt-convolution-mod-prime)
- [Section U: Computational Geometry](#section-u-computational-geometry)
- [U.1 Geometry Primitives + Convex Hull](#u1-geometry-primitives-convex-hull)
- [Section V: Offline Queries](#section-v-offline-queries)
- [V.1 Mo's Algorithm](#v1-mo-s-algorithm)
- [Section W: Randomized DS/Algo](#section-w-randomized-ds-algo)
- [W.1 Randomized Treap](#w1-randomized-treap)
- [Section X: NP-Complete / Approx](#section-x-np-complete-approx)
- [X.1 Bitmask TSP (Exact)](#x1-bitmask-tsp-exact)
- [X.2 Vertex Cover 2-Approx](#x2-vertex-cover-2-approx)
- [X.3 Set Cover Greedy (ln n Approx)](#x3-set-cover-greedy-ln-n-approx)
- [Section Y: Branch and Bound](#section-y-branch-and-bound)
- [Y.1 0/1 Knapsack (Branch and Bound)](#y1-0-1-knapsack-branch-and-bound)
- [Y.2 TSP (Branch and Bound)](#y2-tsp-branch-and-bound)

---

## Section S: Network Flow

---

### S.1 Dinic's Max Flow

```java
import java.util.*;

public class Dinic {
    static final class Edge {
        int to;
        int rev;
        long cap;
        Edge(int to, int rev, long cap) {
            this.to = to;
            this.rev = rev;
            this.cap = cap;
        }
    }

    final int n;
    final List<Edge>[] g;
    final int[] level;
    final int[] it;

    @SuppressWarnings("unchecked")
    public Dinic(int n) {
        this.n = n;
        this.g = (List<Edge>[]) new List[n];
        for (var i = 0; i < n; i++) g[i] = new ArrayList<>();
        this.level = new int[n];
        this.it = new int[n];
    }

    public void addEdge(int fr, int to, long cap) {
        var fwd = new Edge(to, g[to].size(), cap);
        var rev = new Edge(fr, g[fr].size(), 0);
        g[fr].add(fwd);
        g[to].add(rev);
    }

    public long maxFlow(int s, int t) {
        long flow = 0;
        while (bfs(s, t)) {
            Arrays.fill(it, 0);
            for (long pushed; (pushed = dfs(s, t, Long.MAX_VALUE)) != 0; ) {
                flow += pushed;
            }
        }
        return flow;
    }

    private boolean bfs(int s, int t) {
        Arrays.fill(level, -1);
        var q = new ArrayDeque<Integer>();
        level[s] = 0;
        q.add(s);
        while (!q.isEmpty()) {
            var v = q.poll();
            for (var e : g[v]) {
                if (e.cap <= 0 || level[e.to] != -1) continue;
                level[e.to] = level[v] + 1;
                q.add(e.to);
            }
        }
        return level[t] != -1;
    }

    private long dfs(int v, int t, long f) {
        if (v == t) return f;
        for (int i = it[v]; i < g[v].size(); i++, it[v] = i) {
            var e = g[v].get(i);
            if (e.cap <= 0 || level[e.to] != level[v] + 1) continue;
            var pushed = dfs(e.to, t, Math.min(f, e.cap));
            if (pushed == 0) continue;
            e.cap -= pushed;
            g[e.to].get(e.rev).cap += pushed;
            return pushed;
        }
        return 0;
    }
}
```

---

### S.2 Min-Cost Max-Flow

```java
import java.util.*;

public class MinCostMaxFlow {
    static final class Edge {
        int to, rev;
        int cap;
        int cost;
        Edge(int to, int rev, int cap, int cost) {
            this.to = to;
            this.rev = rev;
            this.cap = cap;
            this.cost = cost;
        }
    }

    final int n;
    final List<Edge>[] g;
    final int[] dist;
    final int[] pvV;
    final int[] pvE;
    final boolean[] inQ;

    @SuppressWarnings("unchecked")
    public MinCostMaxFlow(int n) {
        this.n = n;
        g = (List<Edge>[]) new List[n];
        for (var i = 0; i < n; i++) g[i] = new ArrayList<>();
        dist = new int[n];
        pvV = new int[n];
        pvE = new int[n];
        inQ = new boolean[n];
    }

    public void addEdge(int u, int v, int cap, int cost) {
        var a = new Edge(v, g[v].size(), cap, cost);
        var b = new Edge(u, g[u].size(), 0, -cost);
        g[u].add(a);
        g[v].add(b);
    }

    // returns {flow, cost}
    public int[] minCostMaxFlow(int s, int t) {
        var flow = 0;
        var cost = 0;
        final int INF = 1_000_000_000;
        while (true) {
            Arrays.fill(dist, INF);
            Arrays.fill(inQ, false);
            dist[s] = 0;
            var q = new ArrayDeque<Integer>();
            q.add(s);
            inQ[s] = true;
            while (!q.isEmpty()) {
                var u = q.poll();
                inQ[u] = false;
                for (var i = 0; i < g[u].size(); i++) {
                    var e = g[u].get(i);
                    if (e.cap <= 0) continue;
                    var nd = dist[u] + e.cost;
                    if (nd < dist[e.to]) {
                        dist[e.to] = nd;
                        pvV[e.to] = u;
                        pvE[e.to] = i;
                        if (!inQ[e.to]) {
                            inQ[e.to] = true;
                            q.add(e.to);
                        }
                    }
                }
            }

            if (dist[t] == INF) break;
            var add = INF;
            for (var v = t; v != s; v = pvV[v]) {
                var e = g[pvV[v]].get(pvE[v]);
                add = Math.min(add, e.cap);
            }
            for (var v = t; v != s; v = pvV[v]) {
                var e = g[pvV[v]].get(pvE[v]);
                e.cap -= add;
                g[v].get(e.rev).cap += add;
                cost += add * e.cost;
            }
            flow += add;
        }
        return new int[]{flow, cost};
    }
}
```

---

## Section T: FFT / NTT

---

### T.1 FFT Convolution (Complex)

```java
import java.util.*;

public class FFTConvolution {
    static final class C {
        double re, im;
        C(double re, double im) { this.re = re; this.im = im; }
        C add(C o) { return new C(re + o.re, im + o.im); }
        C sub(C o) { return new C(re - o.re, im - o.im); }
        C mul(C o) { return new C(re * o.re - im * o.im, re * o.im + im * o.re); }
    }

    public static long[] convolution(long[] a, long[] b) {
        var n1 = a.length;
        var n2 = b.length;
        var n = 1;
        while (n < n1 + n2 - 1) n <<= 1;
        var fa = new C[n];
        var fb = new C[n];
        for (var i = 0; i < n; i++) {
            fa[i] = new C(i < n1 ? a[i] : 0, 0);
            fb[i] = new C(i < n2 ? b[i] : 0, 0);
        }
        fft(fa, false);
        fft(fb, false);
        for (var i = 0; i < n; i++) fa[i] = fa[i].mul(fb[i]);
        fft(fa, true);
        var res = new long[n1 + n2 - 1];
        for (var i = 0; i < res.length; i++) res[i] = Math.round(fa[i].re);
        return res;
    }

    private static void fft(C[] a, boolean inv) {
        var n = a.length;
        for (int i = 1, j = 0; i < n; i++) {
            var bit = n >>> 1;
            for (; (j & bit) != 0; bit >>>= 1) j ^= bit;
            j ^= bit;
            if (i < j) {
                var t = a[i]; a[i] = a[j]; a[j] = t;
            }
        }

        for (int len = 2; len <= n; len <<= 1) {
            var ang = 2 * Math.PI / len * (inv ? -1 : 1);
            var wlen = new C(Math.cos(ang), Math.sin(ang));
            for (int i = 0; i < n; i += len) {
                var w = new C(1, 0);
                for (int j = 0; j < len / 2; j++) {
                    var u = a[i + j];
                    var v = a[i + j + len / 2].mul(w);
                    a[i + j] = u.add(v);
                    a[i + j + len / 2] = u.sub(v);
                    w = w.mul(wlen);
                }
            }
        }

        if (inv) {
            for (var i = 0; i < n; i++) {
                a[i].re /= n;
                a[i].im /= n;
            }
        }
    }
}
```

---

### T.2 NTT Convolution (Mod Prime)

```java
import java.util.*;

public class NTTConvolution {
    // 998244353 = 119*2^23 + 1, primitive root = 3
    static final int MOD = 998244353;
    static final int G = 3;

    public static int[] convolution(int[] a, int[] b) {
        var n1 = a.length;
        var n2 = b.length;
        var n = 1;
        while (n < n1 + n2 - 1) n <<= 1;
        var fa = Arrays.copyOf(a, n);
        var fb = Arrays.copyOf(b, n);
        ntt(fa, false);
        ntt(fb, false);
        for (var i = 0; i < n; i++) fa[i] = (int) ((long) fa[i] * fb[i] % MOD);
        ntt(fa, true);
        return Arrays.copyOf(fa, n1 + n2 - 1);
    }

    private static void ntt(int[] a, boolean inv) {
        var n = a.length;
        for (int i = 1, j = 0; i < n; i++) {
            var bit = n >>> 1;
            for (; (j & bit) != 0; bit >>>= 1) j ^= bit;
            j ^= bit;
            if (i < j) {
                var t = a[i]; a[i] = a[j]; a[j] = t;
            }
        }

        for (int len = 2; len <= n; len <<= 1) {
            var wlen = modPow(G, (MOD - 1) / len);
            if (inv) wlen = modInv(wlen);
            for (int i = 0; i < n; i += len) {
                long w = 1;
                for (int j = 0; j < len / 2; j++) {
                    var u = a[i + j];
                    var v = (int) (w * a[i + j + len / 2] % MOD);
                    var x = u + v;
                    if (x >= MOD) x -= MOD;
                    var y = u - v;
                    if (y < 0) y += MOD;
                    a[i + j] = x;
                    a[i + j + len / 2] = y;
                    w = w * wlen % MOD;
                }
            }
        }

        if (inv) {
            var invN = modInv(n);
            for (var i = 0; i < n; i++) a[i] = (int) ((long) a[i] * invN % MOD);
        }
    }

    private static int modPow(int a, int e) {
        long r = 1, x = a;
        while (e > 0) {
            if ((e & 1) == 1) r = r * x % MOD;
            x = x * x % MOD;
            e >>= 1;
        }
        return (int) r;
    }

    private static int modInv(int a) {
        return modPow(a, MOD - 2);
    }
}
```

---

## Section U: Computational Geometry

---

### U.1 Geometry Primitives + Convex Hull

```java
import java.util.*;

public class Geometry {
    public record P(long x, long y) {}

    public static long cross(P a, P b, P c) {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    public static int orient(P a, P b, P c) {
        return Long.compare(cross(a, b, c), 0);
    }

    public static boolean onSegment(P a, P b, P p) {
        if (cross(a, b, p) != 0) return false;
        return Math.min(a.x, b.x) <= p.x && p.x <= Math.max(a.x, b.x)
            && Math.min(a.y, b.y) <= p.y && p.y <= Math.max(a.y, b.y);
    }

    public static boolean segmentsIntersect(P a, P b, P c, P d) {
        var o1 = orient(a, b, c);
        var o2 = orient(a, b, d);
        var o3 = orient(c, d, a);
        var o4 = orient(c, d, b);
        if (o1 == 0 && onSegment(a, b, c)) return true;
        if (o2 == 0 && onSegment(a, b, d)) return true;
        if (o3 == 0 && onSegment(c, d, a)) return true;
        if (o4 == 0 && onSegment(c, d, b)) return true;
        return o1 != o2 && o3 != o4;
    }

    public static List<P> convexHull(List<P> pts) {
        var p = new ArrayList<>(pts);
        p.sort(Comparator.comparingLong(P::x).thenComparingLong(P::y));
        if (p.size() <= 1) return p;

        var lo = new ArrayList<P>();
        for (var pt : p) {
            while (lo.size() >= 2 && cross(lo.get(lo.size() - 2), lo.get(lo.size() - 1), pt) <= 0) lo.remove(lo.size() - 1);
            lo.add(pt);
        }
        var up = new ArrayList<P>();
        for (var i = p.size() - 1; i >= 0; i--) {
            var pt = p.get(i);
            while (up.size() >= 2 && cross(up.get(up.size() - 2), up.get(up.size() - 1), pt) <= 0) up.remove(up.size() - 1);
            up.add(pt);
        }
        lo.remove(lo.size() - 1);
        up.remove(up.size() - 1);
        lo.addAll(up);
        return lo;
    }
}
```

---

## Section V: Offline Queries

---

### V.1 Mo's Algorithm

```java
import java.util.*;

public class MosAlgorithm {
    public record Query(int l, int r, int idx) {}

    // Example skeleton: range sum via add/remove.
    public static long[] solve(int[] a, Query[] qs) {
        var n = a.length;
        var block = Math.max(1, (int) Math.sqrt(n));
        Arrays.sort(qs, (x, y) -> {
            var bx = x.l() / block;
            var by = y.l() / block;
            if (bx != by) return Integer.compare(bx, by);
            if ((bx & 1) == 0) return Integer.compare(x.r(), y.r());
            return Integer.compare(y.r(), x.r());
        });

        var ans = new long[qs.length];
        int L = 0, R = -1;
        long cur = 0;

        for (var qu : qs) {
            var l = qu.l();
            var r = qu.r();
            while (L > l) cur += a[--L];
            while (R < r) cur += a[++R];
            while (L < l) cur -= a[L++];
            while (R > r) cur -= a[R--];
            ans[qu.idx()] = cur;
        }
        return ans;
    }
}
```

---

## Section W: Randomized DS/Algo

---

### W.1 Randomized Treap

```java
import java.util.*;

public class Treap {
    static final class Node {
        int key;
        int pr;
        int sz;
        Node l, r;
        Node(int key, int pr) {
            this.key = key;
            this.pr = pr;
            this.sz = 1;
        }
    }

    static final Random rng = new Random(1);

    static int size(Node t) { return t == null ? 0 : t.sz; }
    static void pull(Node t) { if (t != null) t.sz = 1 + size(t.l) + size(t.r); }

    // splits into (<=key, >key)
    static Node[] split(Node t, int key) {
        if (t == null) return new Node[]{null, null};
        if (t.key <= key) {
            var sp = split(t.r, key);
            t.r = sp[0];
            pull(t);
            return new Node[]{t, sp[1]};
        } else {
            var sp = split(t.l, key);
            t.l = sp[1];
            pull(t);
            return new Node[]{sp[0], t};
        }
    }

    static Node merge(Node a, Node b) {
        if (a == null) return b;
        if (b == null) return a;
        if (a.pr > b.pr) {
            a.r = merge(a.r, b);
            pull(a);
            return a;
        } else {
            b.l = merge(a, b.l);
            pull(b);
            return b;
        }
    }

    static Node insert(Node t, int key) {
        if (contains(t, key)) return t;
        var n = new Node(key, rng.nextInt());
        var sp = split(t, key);
        return merge(merge(sp[0], n), sp[1]);
    }

    static Node erase(Node t, int key) {
        if (t == null) return null;
        if (key == t.key) return merge(t.l, t.r);
        if (key < t.key) t.l = erase(t.l, key);
        else t.r = erase(t.r, key);
        pull(t);
        return t;
    }

    static boolean contains(Node t, int key) {
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.l : t.r;
        }
        return false;
    }
}
```

---

## Section X: NP-Complete / Approx

---

### X.1 Bitmask TSP (Exact)

```java
import java.util.*;

public class BitmaskTSP {
    // dist: n x n, returns min Hamiltonian cycle starting/ending at 0.
    public static long solve(long[][] dist) {
        var n = dist.length;
        var N = 1 << n;
        var INF = (long) 4e18;
        var dp = new long[N][n];
        for (var i = 0; i < N; i++) Arrays.fill(dp[i], INF);
        dp[1][0] = 0;

        for (var mask = 1; mask < N; mask++) {
            for (var u = 0; u < n; u++) {
                var cur = dp[mask][u];
                if (cur >= INF) continue;
                for (var v = 0; v < n; v++) {
                    if (((mask >> v) & 1) == 1) continue;
                    var nm = mask | (1 << v);
                    dp[nm][v] = Math.min(dp[nm][v], cur + dist[u][v]);
                }
            }
        }

        var best = INF;
        var full = N - 1;
        for (var u = 0; u < n; u++) best = Math.min(best, dp[full][u] + dist[u][0]);
        return best;
    }
}
```

---

### X.2 Vertex Cover 2-Approx

```java
public class VertexCoverApprox {
    // 2-approx via maximal matching: pick both endpoints.
    public static boolean[] cover(int n, int[][] edges) {
        var pick = new boolean[n];
        for (var e : edges) {
            var u = e[0];
            var v = e[1];
            if (pick[u] || pick[v]) continue;
            pick[u] = true;
            pick[v] = true;
        }
        return pick;
    }
}
```

---

### X.3 Set Cover Greedy (ln n Approx)

```java
import java.util.*;

public class SetCoverGreedy {
    // universe size U, sets: list of int[] elements (0..U-1)
    public static List<Integer> solve(int U, List<int[]> sets) {
        var covered = new boolean[U];
        var remain = U;
        var picked = new ArrayList<Integer>();
        var used = new boolean[sets.size()];

        while (remain > 0) {
            int best = -1;
            int bestGain = 0;
            for (var i = 0; i < sets.size(); i++) {
                if (used[i]) continue;
                var gain = 0;
                for (var x : sets.get(i)) if (!covered[x]) gain++;
                if (gain > bestGain) {
                    bestGain = gain;
                    best = i;
                }
            }
            if (best == -1 || bestGain == 0) break;
            used[best] = true;
            picked.add(best);
            for (var x : sets.get(best)) {
                if (!covered[x]) {
                    covered[x] = true;
                    remain--;
                }
            }
        }
        return picked;
    }
}
```

---

## Section Y: Branch and Bound

---

### Y.1 0/1 Knapsack (Branch and Bound)

```java
import java.util.*;

public class KnapsackBranchAndBound {

    public record Item(int w, int v) {}

    static final class Node implements Comparable<Node> {
        int idx;
        int w;
        int v;
        double bound;
        @Override public int compareTo(Node o) { return Double.compare(o.bound, this.bound); }
    }

    public static int solve(Item[] items, int capacity) {
        var it = items.clone();
        Arrays.sort(it, (a, b) -> Double.compare((double) b.v() / b.w(), (double) a.v() / a.w()));

        var pq = new PriorityQueue<Node>();
        var root = new Node();
        root.idx = 0;
        root.w = 0;
        root.v = 0;
        root.bound = bound(root, it, capacity);
        pq.add(root);

        var best = 0;
        while (!pq.isEmpty()) {
            var cur = pq.poll();
            if (cur.bound <= best) continue;
            if (cur.idx == it.length) {
                best = Math.max(best, cur.v);
                continue;
            }

            // include
            var in = new Node();
            in.idx = cur.idx + 1;
            in.w = cur.w + it[cur.idx].w();
            in.v = cur.v + it[cur.idx].v();
            if (in.w <= capacity) {
                best = Math.max(best, in.v);
                in.bound = bound(in, it, capacity);
                if (in.bound > best) pq.add(in);
            }

            // exclude
            var ex = new Node();
            ex.idx = cur.idx + 1;
            ex.w = cur.w;
            ex.v = cur.v;
            ex.bound = bound(ex, it, capacity);
            if (ex.bound > best) pq.add(ex);
        }
        return best;
    }

    private static double bound(Node n, Item[] it, int cap) {
        if (n.w >= cap) return 0;
        var value = (double) n.v;
        var weight = n.w;
        var i = n.idx;
        while (i < it.length && weight + it[i].w() <= cap) {
            weight += it[i].w();
            value += it[i].v();
            i++;
        }
        if (i < it.length) {
            value += (cap - weight) * ((double) it[i].v() / it[i].w());
        }
        return value;
    }
}
```

---

### Y.2 TSP (Branch and Bound)

```java
import java.util.*;

public class TSPBranchAndBound {
    static final class Node implements Comparable<Node> {
        int last;
        int mask;
        long cost;
        long bound;
        int[] path;
        int len;
        @Override public int compareTo(Node o) { return Long.compare(this.bound, o.bound); }
    }

    // dist must be complete; use large number for missing edges.
    public static long solve(long[][] dist) {
        var n = dist.length;
        var minOut = new long[n];
        Arrays.fill(minOut, Long.MAX_VALUE);
        for (var i = 0; i < n; i++) {
            for (var j = 0; j < n; j++) if (i != j) minOut[i] = Math.min(minOut[i], dist[i][j]);
        }

        var pq = new PriorityQueue<Node>();
        var root = new Node();
        root.last = 0;
        root.mask = 1;
        root.cost = 0;
        root.path = new int[n + 1];
        root.path[0] = 0;
        root.len = 1;
        root.bound = bound(root, dist, minOut);
        pq.add(root);

        var best = Long.MAX_VALUE;
        while (!pq.isEmpty()) {
            var cur = pq.poll();
            if (cur.bound >= best) continue;
            if (cur.mask == (1 << n) - 1) {
                var total = cur.cost + dist[cur.last][0];
                best = Math.min(best, total);
                continue;
            }

            for (var nxt = 0; nxt < n; nxt++) {
                if (((cur.mask >> nxt) & 1) == 1) continue;
                var nn = new Node();
                nn.last = nxt;
                nn.mask = cur.mask | (1 << nxt);
                nn.cost = cur.cost + dist[cur.last][nxt];
                nn.path = cur.path.clone();
                nn.path[cur.len] = nxt;
                nn.len = cur.len + 1;
                nn.bound = bound(nn, dist, minOut);
                if (nn.bound < best) pq.add(nn);
            }
        }
        return best;
    }

    // Simple admissible bound: cost so far + sum of min outgoing edges for each unvisited node + min edge from last to some unvisited.
    private static long bound(Node n, long[][] dist, long[] minOut) {
        long b = n.cost;
        var N = dist.length;
        for (var i = 0; i < N; i++) {
            if (((n.mask >> i) & 1) == 0) b += minOut[i];
        }
        // ensure we can leave current last if not finished
        if (n.mask != (1 << N) - 1) b += minOut[n.last];
        return b;
    }
}
```
