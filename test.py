import logic
from util import *

E = Predicate("E")
B = Predicate("B")

a,b,c,d,x,y,z,p,q,r,s = Vars("a b c d x y z p q r s")

A1 = Forall([a, b], E(a,b,b,a))
A2 = Forall([a,b,p,q,r,s], Impl(And(E(a,b,p,q), E(a,b,r,s)), E(p,q,r,s)))
A3 = Forall([a,b,c], Impl(E(a,b,c,c), Eq(a,b)))
A4 = Forall([a,q,b,c],
       Exists([x],
         And(B(q,a,x), E(a,x,b,c))
       ))
A6 = Forall([a, b], Impl(B(a,b,a), Eq(a,b)))
A7 = Forall([a,b,p,q,z], Impl(
    And(B(a,p,z), B(p,q,z)),
    Exists([x], And(B(p,x,b), B(q,x,a)))
))

Satz2_1 = Forall([x,y], E(x,y,x,y))
print(solve(
    [A1, A2], Satz2_1
))
print()

Satz2_2 = Forall([a,b,c,d], Impl(E(a,b,c,d), E(c,d,a,b)))
print(solve(
    [A2, Satz2_1], Satz2_2
))

Satz2_8 = Forall([a,b], E(a,a,b,b))
print(solve(
    [A1, A2, A3, A4, A6], Satz2_8
)) #!
