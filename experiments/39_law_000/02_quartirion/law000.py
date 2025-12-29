import math

def q_add(q, dq):
    return (
        q[0] + dq[0],
        q[1] + dq[1],
        q[2] + dq[2],
        q[3] + dq[3],
    )

def q_norm(q):
    a, b, c, d = q
    n = math.sqrt(a*a + b*b + c*c + d*d)
    if n == 0:
        return (1.0, 0.0, 0.0, 0.0)
    return (a/n, b/n, c/n, d/n)

def apply_law000(graph, state, tick):
    new_state = {}

    # chaos injector: ±1 podle ticku
    chaos = -1 if (tick & 1) else +1

    for node, neighbors in graph.items():
        # spočítáme "kvaternionový posun" z aktivních sousedů
        # (čistě algebraický, žádná trigonometrie)
        dq = [0.0, 0.0, 0.0, 0.0]

        for n in neighbors:
            a, b, c, d = state[n]
            # imaginární část sousedů tvoří směr posunu
            dq[1] += b
            dq[2] += c
            dq[3] += d

        # chaos přidáme do reálné části
        dq[0] += 0.05 * chaos

        # zmenšíme krok, aby evoluce byla hladká
        dq = tuple(x * 0.1 for x in dq)

        # update = starý stav + posun
        updated = q_add(state[node], dq)

        # renormalizace = fundamentální omezení
        new_state[node] = q_norm(updated)

    return new_state
