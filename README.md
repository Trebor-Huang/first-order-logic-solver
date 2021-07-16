# first-order-logic-solver
A simple first order logic solver

# Internal Representation

Uses a locally nameless approach.

A uniform `Bind` node is used for every binding, including `forall`, `exists`.

Uses tuples to ease pattern matching in Python. The first component signifies the type of nodes, and the rest contains additional information or subtrees.

A conjunctive normal form is represented by a `frozenset` of disjunctive clauses, together with justifications for each of them.

# Algorithm

Naive resolution and paramodulation is used.

# REPL

Provides a simple interface to introduce functions and predicates, state axioms, produce step by step proofs. Each of the steps just states an implication of the previously proved statements -- the implication is checked by the machine.


