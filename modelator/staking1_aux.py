import random

"""
Dirty prototype of trace selection algorithm

Algorithm:

Input: a set of n traces and a projection algorithm mapping a trace to a set of some type 
Output: a set of m pairwise unique traces minimizing a loss function with m < n

Pseudocode:
    Sample a population G of m traces uniformly from the search space (the set of all possible valid sets of size m)
    Repeat as desired:
        Choose sx, sy from G
        sx', sy' = crossover(sx, sy, p)
        sx'' = mutate(sx')
        sy'' = mutate(sy')
        if valid(sx'') and valid(sy'') /\ min(loss(sx''),loss(sy'')) <= min(loss(sx), loss(sy)):
            sx := sx''
            sy := sy''
    Choose best and return the best set of traces from G according to loss

loss(s: set of m traces) = sum(similiarity(ti,tj)) for ti,tj in s, i#j

similarity(ti, tj) = cardinality(project(ti) intersect project(tj))/cardinality(project(ti) union project(tj))
"""


def pprint(s):
    print(s, flush=True)


PARAM_population_size = 50
PARAM_target_size = 64
PARAM_crossover_probability = 0.75
PARAM_iterations = 160000
PARAM_info_interval = 16000


def select_subset(list_of_sets, target_size=PARAM_target_size):

    N = len(list_of_sets)

    def crossover(vx, vy):
        vx, vy = list(vx), list(vy)
        n = len(vx)
        assert len(vy) == n
        r = random.choice(range(1, n - 1))
        for i in range(r, n):
            vx[i], vy[i] = vy[i], vx[i]
        return vx, vy

    def mutate(v):
        v = list(v)
        n = len(v)
        P = 1 / n
        for i in range(n):
            if random.uniform(0, 1) < P:
                v[i] = random.choice(range(N))
        return v

    def valid(v):
        return len(set(v)) == len(v)

    def loss(v):
        def similarity_f(A, B):
            intersect = A.intersection(B)
            union = A.union(B)
            return round(len(intersect) / len(union), 3)

        x = 0
        for i in range(len(v) - 1):
            for j in range(i + 1, len(v)):
                x += similarity_f(list_of_sets[v[i]], list_of_sets[v[j]])
        return x

    # Initialize population
    G = [None] * PARAM_population_size
    G_ixs = list(range(len(G)))
    for i in G_ixs:
        G[i] = random.sample(range(N), target_size)

    def best():
        best_ix = 0
        best_loss = loss(G[0])
        for i in range(1, len(G)):
            value = loss(G[i])
            if value < best_loss:
                best_ix = i
                best_loss = value
        return G[best_ix], best_loss

    _, random_choice_loss = best()

    for k in range(PARAM_iterations):
        sxi, syi = random.sample(G_ixs, 2)
        sx = list(G[sxi])
        sy = list(G[syi])
        if random.uniform(0, 1) < PARAM_crossover_probability:
            sx, sy = crossover(sx, sy)
        sx = mutate(sx)
        sy = mutate(sy)
        if valid(sx) and valid(sy):
            if min(loss(sx), loss(sy)) <= min(loss(G[sxi]), loss(G[syi])):
                G[sxi] = sx
                G[syi] = sy
        if k % PARAM_info_interval == 0:
            _, best_value = best()
            pprint(f"loss: {best_value}")

    indexes_of_best_sets, loss_value = best()
    return indexes_of_best_sets, loss_value, random_choice_loss
