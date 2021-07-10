import syntax, re
import logic

class Expects(Exception):
    def __init__(self, ex, get):
        if len(ex) == 1:
            super().__init__(f"Expects {repr(ex[0])}, got {repr(get)}.")
        else:
            super().__init__(f"Expects one of {', '.join(repr(e) for e in ex)}, got {repr(get)}.")

# wff = (quantification)* implication #! push right
# implication = (disjunction ("->" | "→"))* disjunction #! right associative
# disjunction = (conjunction ("\/" | "or" | "|"))* conjunction
# conjunction = (negation ("/\" | "and" | "&"))* negation
# negation = ("not" | "¬")* atomic #! push right
# atomic = equality | predicate_formula | "(" wff ")"
# equality = term "=" term
# predicate_formula = (predicate "(" (term ",")* term ")") | predicate
# term = function_term | variable
# function_term = (function "(" (term ",")* term ")") | variable #!! should be function
# quantification = (forall | exists) variable+ "."
# forall = "forall" | "∀"
# exists = "exists" | "∃"

# variable = literal
# predicate = predeclared literal
# function = predeclared literal

# literal = [A-Za-z][A-Za-z0-9_']*

# It is ambiguous. Free variables that has the same name as functions will be replaced

class Parser:
    def __init__(self, predicates, functions):
        self.predicates = predicates
        self.functions = functions

    def parse(self, source:str):
        self.source = source
        try:
            wff = self.wff()
            syntax.substitute_dict(wff, {f: ("Function", f) for f in self.functions})
            return wff, self.source
        except Expects as e:
            raise e

    def consume(self, *chars_list):
        self.source = self.source.lstrip()
        for chars in chars_list:
            if self.source.startswith(chars):
                self.source = self.source[len(chars):]
                return chars
        raise Expects(chars_list, self.source[:5])

    def take_while(self, func):
        takes = []
        while True:
            try:
                source = self.source
                takes.append(func())
            except:
                self.source = source
                return takes

    def with_sep(self, func, seps):
        def f():
            s = func()
            self.consume(*seps)
            return s
        return f

    def wff(self):
        quants = self.take_while(self.quantification)
        i = self.implication()
        while quants:
            q, v = quants.pop()
            while v:
                v0 = v.pop()
                i = (q, ("Bind", syntax.abstract(i, v0)))
        return i

    def implication(self):
        disjs = self.take_while(self.with_sep(self.disjunction, ["->", "→"]))
        d = self.disjunction()
        while disjs:
            d0 = disjs.pop()
            d = ("implies", d0, d)
        return d

    def disjunction(self):
        conjs = self.take_while(self.with_sep(self.conjunction, ["\\/", "|", "∨"]))
        c = self.conjunction()
        while conjs:
            c0 = conjs.pop()
            c = ("or", c0, c)
        return c

    def conjunction(self):
        negs = self.take_while(self.with_sep(self.negation, ["/\\", "&", "∧"]))
        n = self.negation()
        while negs:
            n0 = negs.pop()
            n = ("and", n0, n)
        return n

    def negation(self):
        negs = self.take_while(lambda : self.consume("~", "¬"))
        a = self.atomic()
        for _ in negs:
            a = ("not", a)
        return a

    def atomic(self):
        try:
            source = self.source
            return self.equality()
        except: 
            try:
                self.source = source
                return self.predicate_formula()
            except: 
                self.source = source
                self.consume("(")
                w = self.wff()
                self.consume(")")
                return w

    def equality(self):
        t1 = self.term()
        self.consume("=")
        t2 = self.term()
        return ("equals", t1, t2)

    def predicate_formula(self):
        p = self.consume(*self.predicates)
        try:
            source = self.source
            self.consume("(")
            args = self.take_while(self.with_sep(self.term, [","]))
            arg = self.term()
            self.consume(")")
            return ("Predicate", p, *args, arg)
        except:
            self.source = source
            return ("Predicate", p)

    def term(self):
        try:
            source = self.source
            return self.function_term()
        except:
            self.source = source
            l = self.literal()
            return ("FVar", l)

    def function_term(self):
        f = self.consume(*self.functions)
        self.consume("(")
        args = self.take_while(self.with_sep(self.term, [","]))
        arg = self.term()
        self.consume(")")
        return ("Function", f, *args, arg)

    def quantification(self):
        q = self.consume("forall", "∀", "exists", "∃")
        if q in ("forall", "∀"):
            q = "forall"
        else:
            q = "exists"
        varnames = self.take_while(self.literal)
        if len(varnames) == 0:
            raise Expects(["[one or more variable identifiers]"], self.source[:5])
        self.consume(".")
        return q, varnames

    literal_regex = re.compile("(?!(forall|exists))[A-Za-z][A-Za-z0-9'_]*")
    def literal(self):
        self.source = self.source.lstrip()
        m = self.literal_regex.match(self.source)
        if m:
            self.source = self.source[m.end():]
            return m.string[:m.end()]
        else:
            raise Expects(["[an identifier]"], self.source[:5])

if __name__ == "__main__":
    parser = Parser(["P", "Q"], ["f"])
    expr = r"forall x y. ~ P(x) /\ ((Q(f(y)) \/ (x = f(y)))) -> Q(f(x)) -> P"
    print(logic.pretty(parser.parse(expr)[0]))
