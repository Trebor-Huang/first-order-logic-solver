# ("FVar", name)
# ("BVar", n)
# ("Bind", expr)
# ("...", ...)

def pretty(node):
    if isinstance(node, tuple) and isinstance(node[0], str):
        return "(" + node[0] + " " + " ".join(pretty(i) for i in node[1:]) + ")"
    else:
        return str(node)

def recur(methods):
    def _recur(node):
        if isinstance(node, tuple) and isinstance(node[0], str):
            if node[0] in methods:
                return methods[node[0]](_recur, node)
            elif "default" in methods:
                return methods["default"](_recur, node)
            else:
                return tuple(_recur(n) for n in node)
        else:
            return node
    return _recur

def instantiate(node, expr, k=0):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "BVar":
            if node[1] == k:
                return expr
            else:
                return node
        elif node[0] == "Bind":
            return ("Bind", instantiate(node[1], expr, k+1))
        else:
            return tuple(instantiate(i, expr, k) for i in node)
    else:
        return node

def abstract(node, name, k=0):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "FVar":
            if node[1] == name:
                return ("BVar", k)
            else:
                return node
        elif node[0] == "Bind":
            return ("Bind", abstract(node[1], name, k+1))
        else:
            return tuple(abstract(i, name, k) for i in node)
    else:
        return node

def substitute(node, name, expr):
    return instantiate(abstract(node, name), expr)

def substitute_dict(node, sigma):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "FVar":
            if node[1] in sigma:
                return sigma[node[1]]
            else:
                return node
        else:
            return tuple(substitute_dict(i, sigma) for i in node)
    else:
        return node

def free(node):
    if isinstance(node, tuple) and isinstance(node[0], str):
        if node[0] == "FVar":
            return set(node[1])
        else:
            return set.union(*(free(n) for n in node))
    else:
        return set()

counter = 0
def fresh():
    global counter
    counter += 1
    return "_" + str(counter)

if __name__ == "__main__":
    expr = ("Exists",
        ("Bind",
            ("Equals",
                ("BVar", 0),
                ("FVar", "x")
            )
        )
    )
    print(pretty(expr))
    print(pretty(substitute(expr, "x", ("Literal", 0))))
