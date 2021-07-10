import syntax, logic, functools

def And(P, Q):
    return ("and", P, Q)

def Or(P, Q):
    return ("or", P, Q)

def Impl(P, Q):
    return ("implies", P, Q)

def Neg(P):
    return ("not", P)

def Eq(a, b):
    return ("equals", a, b)

def Var(name):
    return ("FVar", name)

def Vars(names):
    return (("FVar", n) for n in names.split())

def Forall(x, P):
    if x:
        return Forall(x[:-1], ("forall", ("Bind", syntax.abstract(P, x[-1][1]))))
    return P

def Exists(x, P):
    if x:
        return Exists(x[:-1], ("exists", ("Bind", syntax.abstract(P, x[-1][1]))))
    return P

def Function(f):
    return lambda *args: ("Function", f, *args)

def Predicate(P):
    return lambda *args: ("Predicate", P, *args)

def solve(prem, concl):
    if not prem:
        clauses = Neg(concl)
    else:
        clauses = And(Neg(concl), functools.reduce(And, prem))
    return logic.resolution(logic.cnf(clauses))

if __name__ == "__main__":
    P = Predicate("P")
    f = Function("f")
    g = Function("g")
    u, v, w, x = Vars("u v w x")
    c1 = Or(P(u), P(f(u)))
    c2 = Impl(P(v), P(f(w)))
    c3 = And(P(x), P(f(x)))
    # print(solve([c1, c2], c3))
    c4 = P(f())
    c5 = Eq(f(), g())
    c6 = P(g())
    print(solve([c4, c5], c6))
    print(solve([], Exists([x],Or(Neg(P(x)), Forall([u], P(u))))))
