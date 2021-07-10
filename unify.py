import syntax

def _finished(clauses):
    # Finishes if each free variable appears only once, on all of the LHS
    # print(*clauses, sep="\n", end="\n\n")
    vs = set()
    for L, _ in clauses:
        if L[0] != "FVar" or L[1] in vs:
            return False
        else:
            vs.add(L[1])
    for _, R in clauses:
        if syntax.free(R).intersection(vs):
            return False
    return True

# Inputs a set of tuples (LHS, RHS), outputs dictionary

def unify(*clauses):
    while not _finished(clauses):
        L, R = clauses[0]
        if len(L) > 0 and isinstance(L[0], str) and len(R) > 0 and isinstance(R[0], str):
            if L == R:
                clauses = clauses[1:]
            elif L[0] == "FVar":
                if L[1] in syntax.free(R):
                    return None
                clauses = *((syntax.substitute(Li, L[1], R), syntax.substitute(Ri, L[1], R)) for (Li, Ri) in clauses[1:]), (L, R)
            elif R[0] == "FVar":
                clauses = *clauses[1:], (R, L)
            elif L[0] != R[0]:
                return None
            else:
                if len(L) != len(R):
                    return None
                clauses = clauses[1:]
                for k in range(len(L)):
                    if len(L[k]) > 0 and isinstance(L[k][0], str) and len(R[k]) > 0 and isinstance(R[k][0], str):
                        clauses += ((L[k], R[k]),)
                    elif L[k] != R[k]:
                        return None
        else:
            if L != R:
                return None
            clauses = clauses[1:]
    return {f: r for (_, f), r in clauses}

if __name__ == "__main__":
    print(unify(
        (("F", ("FVar", "x"), ("F", ("FVar", "y"), ("FVar", "z"))), ("F", ("F", ("FVar", "z"), ("FVar", "y")), ("FVar", "x")))
    ))
    print(unify((("Function", "f"), ("Function", "f"))))
