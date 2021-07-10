# Indexes the subterms and literals
# todoo how?

class Indexer:
    def __init__(self, cnf):
        # cnf is an iterable of frozen sets of literals
        self.literal_dict = dict()
        self.subterm_dict = dict()
        for dj in cnf:  # we just need the dj
            for i, l in enumerate(dj):
                self.add_literal(l, (dj,i), self.literal_dict)
                self.add_subterm(l, (dj,i), self.subterm_dict)

    def subterms(self):
        pass

    def literals(self):
        pass

    def add_literal(self, l, c, pos):
        if isinstance(l, tuple) and len(l) > 0 and isinstance(l[0], str):
            # compute branch
            if l[0] == "FVar":
                pos["FVar"] = c
            else:
                if l[0] not in pos:
                    pos[l[0]] = dict()
                # TODO
        else:
            pass

    def add_subterm(self, l, c, pos):
        pass

if __name__ == "__main__":
    pass
