from syntax import *
import unify

# and
# or
# not
# implies
# forall
# exists
# equals
# ("Predicate", name, args...)
# ("Function", name, args...)

pretty = recur(
    {
        "and": lambda r, n: f"({r(n[1])} ∧ {r(n[2])})",
        "or": lambda r, n: f"({r(n[1])} ∨ {r(n[2])})",
        "not": lambda r, n: f"(¬{r(n[1])})",
        "Bind": lambda r, n: f".{r(n[1])}",
        "FVar": lambda r, n: n[1],
        "BVar": lambda r, n: str(n[1]),
        "implies": lambda r, n: f"({r(n[1])} → {r(n[2])})",
        "forall": lambda r, n: f"(∀{r(n[1])})",
        "exists": lambda r, n: f"(∃{r(n[1])})",
        "equals": lambda r, n: f"({r(n[1])} == {r(n[2])})",
        "Predicate": lambda r, n: f"{n[1]}({','.join(r(i) for i in n[2:])})" if len(n) > 2 else n[1],
        "Function": lambda r, n: f"{n[1]}({','.join(r(i) for i in n[2:])})" if len(n) > 2 else n[1],
        "Hole": lambda r, n: "?",
        "default": lambda r, n: str(n)
    }
)


def pretty_clause(clause):
    if not clause:
        return "⊥"
    return " ∨ ".join(pretty(i) if p else "¬" + pretty(i) for i, p in clause)


def pretty_cnf(clauses):
    return "| " + "\n| ".join(pretty_clause(c) for c in clauses) + "\n"


def all_subterm(node):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "Predicate":
            for i, n in enumerate(node[2:]):
                for st, t in all_subterm(n):
                    yield (node[:2+i] + (st,) + node[3+i:], t)
        elif node[0] == "Function":
            yield ("Hole",), node
            for i, n in enumerate(node[2:]):
                for st, t in all_subterm(n):
                    yield (node[:2+i] + (st,) + node[3+i:], t)
        elif node[0] == "FVar":
            yield ("Hole",), node
        elif node[0] == "equals":
            for st, t in all_subterm(node[1]):
                yield ("equals", st, node[2]), t
            for st, t in all_subterm(node[2]):
                yield ("equals", node[1], st), t
        else:
            for i, n in enumerate(node):
                for st, t in all_subterm(n):
                    yield (node[:i] + (st,) + node[1+i:], t)


def substitute_hole(node, term):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "Hole":
            return term
        else:
            return tuple(substitute_hole(i, term) for i in node)
    else:
        return node


elim_impl = recur(
    {
        "implies": lambda r, n: ("or", ("not", r(n[1])), r(n[2]))
    }
)

_neg = recur(
    {
        "and": lambda r, n: ("or", r(n[1]), r(n[2])),
        "or": lambda r, n: ("and", r(n[1]), r(n[2])),
        "not": lambda r, n: n[1],
        "forall": lambda r, n: ("exists", r(n[1])),
        "exists": lambda r, n: ("forall", r(n[1])),
        "Bind": lambda r, n: ("Bind", r(n[1])),
        "default": lambda r, n: ("not", n)
    }
)

neg_in = recur(
    {
        "not": lambda r, n: _neg(r(n[1]))
    }
)

def _elim_exists(clause, context=set()):
    # assumes negations have been pushed in
    if clause[0] == "forall":
        fname = fresh()
        inside = instantiate(clause[1][1], ("FVar", fname))
        new = _elim_exists(
            inside,
            context.union(set((fname,))))
        return ("forall",
                ("Bind",
                 abstract(
                     new,
                     fname)))
    elif clause[0] == "exists":
        fname = fresh()
        inside = instantiate(clause[1][1], ("Function", fname, *context))
        new = _elim_exists(inside, context)
        return new
    elif clause[0] in ["and", "or"]:
        new1 = _elim_exists(clause[1], context)
        new2 = _elim_exists(clause[2], context)
        return (clause[0], new1, new2)
    else:
        return clause


def elim_exists(clause):
    return _elim_exists(clause, free(clause))


def elim_forall(clause):
    # first name all the bound variables differently
    # (∀x. A) and B  <==> (∀x. A and B)
    # (∀x. A) or B   <==> (∀x. A or B)
    # So we can just pull those quantifiers out
    if clause[0] == "forall":
        fname = fresh()
        return elim_forall(instantiate(clause[1][1], ("FVar", fname)))
    elif clause[0] in ["and", "or"]:
        c1 = elim_forall(clause[1])
        c2 = elim_forall(clause[2])
        return (clause[0], c1, c2)
    else:
        return clause


def _cnf(clause):
    # Returns a conjunction of disjunctions (a frozen set of frozen sets)
    if clause[0] == "and":
        return _cnf(clause[1]).union(_cnf(clause[2]))
    elif clause[0] == "or":
        return frozenset(c1.union(c2) for c1 in _cnf(clause[1]) for c2 in _cnf(clause[2]))
    else:
        # atomic, additional check for negatedness
        if clause[0] == "not":
            return frozenset((  # A set
                frozenset(  # of sets
                    ((clause[1], False),)  # of pairs
                ),))
        else:
            return frozenset((  # A set
                frozenset(  # of sets
                    ((clause, True),)  # of pairs
                ),))


def cnf(clause):
    # Given a logical formula, returns a tuple (conjunction) of tuples (disjunctions) of literals
    # The literals are (P, True/False), which means "P is True/False."
    return _cnf(elim_forall(elim_exists(neg_in(elim_impl(clause)))))

class Justification:
    # provides pretty justification
    def __init__(self, conclusion, justification, *premise_justification):
        self.conclusion = conclusion
        self.justification = justification
        self.premises = premise_justification

    def __str__(self):
        return "\n".join("|" + line for p in self.premises for line in str(p).split("\n")) + ("\n" if self.premises else "") + pretty_clause(self.conclusion) + "\t" + self.justification

def _resolution(clauses1, clauses2):
    # Todo pack the literals into an efficient structure
    # Todo deletion strategy
    # resolution:
    # A \/ L1    ~B \/ L2   ==>
    # L1* \/ L2*   where * unifies A&B
    #
    # paramodulation:
    # L[t] \/ L1    r=s \/ L2   ==>
    # L*[s*] \/ L1* \/ L2*   where * unifies t&r
    # Here only 1 instance of t is replaced
    for c1 in clauses1:
        for l1, p1 in c1:
            paramodulation = (p1 and l1[0] == "equals")
            for c2 in clauses2:
                for l2, p2 in c2:
                    if paramodulation and (l1, p1) != (l2, p2):  # paramodulation
                        # paramodulating with itself always yields reflexive equation
                        # but p1 may equal p2
                        for hole, subterm in all_subterm(l2):
                            sigma = unify.unify((l1[1], subterm))
                            if sigma is None:
                                continue
                            new_clause = frozenset.union(
                                frozenset((substitute_dict(l, sigma), p)
                                          for l, p in c1 if l!=l1 and p!=p1),
                                frozenset((substitute_dict(l, sigma), p)
                                          for l, p in c2 if l!=l2 and p!=p2),
                                [(substitute_hole(hole, substitute_dict(l1[2], sigma)), p2)]
                            )
                            yield new_clause, Justification(new_clause, "By paramodulation", clauses1[c1], clauses2[c2])
                    # resolution
                    if p1 == p2:  # we need different polarities
                        continue
                    sigma = unify.unify((l1, l2))
                    if sigma is None:
                        continue
                    new_clause = frozenset((substitute_dict(l, sigma), p) for l, p in c1 if (l, p) != (
                        l1, p1)).union((substitute_dict(l, sigma), p) for l, p in c2 if (l, p) != (l2, p2))
                    yield new_clause, Justification(new_clause, "By resolution", clauses1[c1], clauses2[c2])

def resolution(clauses):
    clauses = {cl: Justification(cl, "Given") for cl in clauses}
    new = {cl: i for cl, i in _resolution(clauses, clauses)}
    while frozenset() not in new and not all(ncl in clauses for ncl in new):
        for ncl in new:
            if not ncl in clauses:
                clauses[ncl] = new[ncl]
        new = {cl: i for cl, i in _resolution(clauses, new)}
    if frozenset() in new:
        return new[frozenset()]
    return False


if __name__ == "__main__":
    print(resolution(frozenset(
        [
            frozenset([
                (("Predicate", "P", ("FVar", "x")), False),
                (("Predicate", "Q", ("FVar", "x")), True)
            ]),
            frozenset([
                (("Predicate", "P", ("Function", "a")), True)
            ]),
            frozenset([
                (("Predicate", "Q", ("Function", "a")), False)
            ])
        ]
    )))
