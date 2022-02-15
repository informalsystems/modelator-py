import json
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
PARAM_iterations = 100000


class Similarity:
    def __init__(self, list_of_sets):
        n = len(list_of_sets)
        self.n = n
        self.store = [0] * ((n * (n - 1)) // 2)
        self.compute(list_of_sets)

    def index(self, i, j):
        ix = i * self.n + j
        ix -= (i * (i + 1)) // 2
        ix -= i + 1
        return ix

    def query(self, i, j):
        if i == j:
            return 1
        if j < i:
            i, j = j, i
        ix = self.index(i, j)
        return self.store[ix]

    def compute(self, list_of_sets):
        def similarity(A, B):
            intersect = A.intersection(B)
            union = A.union(B)
            return round(len(intersect) / len(union), 3)

        for i in range(0, self.n - 1):
            for j in range(i + 1, self.n):
                ix = self.index(i, j)
                self.store[ix] = similarity(list_of_sets[i], list_of_sets[j])


def select_subset(traces, project):

    N = len(traces)
    pprint("Starting")
    projected = [project(t) for t in traces]
    pprint("Finished projecting")
    # similarity = Similarity(projected)
    # pprint("Finished computing similarities")
    # lowest_similarity = sorted(similarity.store)
    # pprint(f"Smallest similarity: {lowest_similarity[0]}")
    # lower_bound = (PARAM_target_size * PARAM_target_size * lowest_similarity[0]) / 2
    # pprint(f"Lower bound on loss: {lower_bound}")

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
                # x += similarity.query(v[i], v[j])
                x += similarity_f(projected[v[i]], projected[v[j]])
        return x

    # Initialize population
    G = [None] * PARAM_population_size
    G_ixs = list(range(len(G)))
    for i in G_ixs:
        G[i] = random.sample(range(N), PARAM_target_size)

    def best():
        best_ix = 0
        best_value = loss(G[0])
        for i in range(1, len(G)):
            value = loss(G[i])
            if value < best_value:
                best_ix = i
                best_value = value
        return G[best_ix], best_value

    _, random_choice_value = best()

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
        if k % 8000 == 0:
            _, best_value = best()
            pprint(best_value)

    best, value = best()
    best_traces = [traces[i] for i in best]
    pprint(f"Loss with random choice                 : {random_choice_value}")
    pprint(f"Loss after genetic selection            : {value}")
    # pprint(f"Ratio worse than theoretical lower bound: {value/lower_bound}")
    pprint(f"Ratio better than random choice         : {value/random_choice_value}")
    return best_traces


def project_to_action_outcome_set(trace):
    def itf(trace):
        s = set()
        for state in trace["states"]:
            nature = state["action"]["nature"]
            outcome = state["outcome"]
            redQsize = len(state["redelegationQ"]["#set"])
            undQsize = len(state["undelegationQ"]["#set"])
            valQsize = len(state["validatorQ"]["#set"])
            # s.add((nature, outcome, redQsize, undQsize, valQsize))
            s.add((nature, outcome))
        return s

    def raw_tla(trace):
        s = set()
        for state in trace:
            outcome = None
            nature = None
            for line in state.split("\n"):
                if "nature" in line:
                    nature = line[line.find(">") :]
                if "outcome" in line:
                    outcome = line[line.find("=") :]
            s.add((nature, outcome))
        return s

    return raw_tla(trace)


def real_traces():
    fn = "tlc.5steps.state_split.json"
    traces = None
    with open(fn, "r") as fd:
        content = fd.read()
        traces = json.loads(content)
        # traces = json.loads(content)["traces"]
    assert traces is not None
    return traces


def debug_traces():
    fn = "debug.json"
    traces = None
    with open(fn, "r") as fd:
        content = fd.read()
        traces = json.loads(content)["traces"]
    assert traces is not None
    return traces


def run():
    pprint("Begin run()")

    traces = real_traces()

    pprint(f"Received {len(traces)} traces as input.")
    # LIM = 40000
    # if LIM < len(traces):
    # pprint("WARNING: you have many traces which may harm performance, cropping")
    # traces = random.sample(traces, LIM)

    result = select_subset(traces, project_to_action_outcome_set)
    fn = "tlc.5steps.state_split.{PARAM_target_size}.json"
    with open(fn, "w") as fd:
        obj = {}
        obj["traces"] = result
        s = json.dumps(obj, indent=4)
        fd.write(s)


if __name__ == "__main__":
    run()
