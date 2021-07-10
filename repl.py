import wffparser, util, logic
IDLE = 0
GOAL = 1
STATES = ["Idle", "Goal"]

class REPL:
    def __init__(self):
        self.parser = wffparser.Parser([], [])
        self.globals = dict()
        self.locals = dict()
        self.state = IDLE
        self.goal = None
        self.goalname = None

    def read(self, line:str):
        """Reads a command.
        Theorem [name] : [wff]  -- Sets goal to prove a theorem.
        Axiom [name] : [wff]  -- Assumes an axiom.
        Have [name] : [wff] by [name]*  -- Proves a step [name]
        QED by [name]* -- finishes
        Define Predicate [name]
        Define Function [name]
        Show  -- Show state
        Abort  -- Go to IDLE
        """
        if line.startswith("Theorem"):
            if self.state != IDLE:
                print("[  ERROR] Unable to state theorem now.")
                return
            try:
                n, w = line[7:].split(":")
                g, r = self.parser.parse(w.strip())
            except wffparser.Expects as e:
                print("[  ERROR] Parse error:", e)
                return
            if r.strip() != '':
                print("[WARNING] Ignoring remainder:", r)
            self.goal = g
            self.goalname = n.strip()
            self.state = GOAL
        elif line.startswith("Axiom"):
            if self.state != IDLE:
                print("[  ERROR] Unable to state axiom now.")
                return
            try:
                n, w = line[5:].split(":")
                g, r = self.parser.parse(w.strip())
            except wffparser.Expects as e:
                print("[  ERROR] Parse error:", e)
                return
            if r.strip() != '':
                print("[WARNING] Ignoring remainder:", r)
            self.globals[n.strip()] = g
        elif line.startswith("QED by"):
            if self.state != GOAL:
                print("[  ERROR] No goal to solve.")
                return
            names = line.split()[2:]
            try:
                s = util.solve([self.find(n) for n in names], self.goal)
            except KeyError as e:
                print("[  ERROR]", e)
                return
            if s:
                print(s)
                self.globals[self.goalname] = self.goal
                self.state = IDLE
                self.goal = None
                self.goalname = None
            else:
                print("[  ERROR] Unable to proceed.")
        elif line.startswith("Define"):
            l = line.split()
            # Check name valid
            if l[1] == "Predicate":
                self.parser.predicates.append(l[2])
            elif l[1] == "Function":
                self.parser.functions.append(l[2])
            else:
                print("[  ERROR] Unknown Command.")
        elif line.startswith("Have"):
            l = line[4:].split("by")
            if len(l) != 2:
                print("[  ERROR] Unknown Command.")
                return
            r, nms = l
            r = r.split(":")
            if len(r) != 2:
                print("[  ERROR] Unknown Command.")
                return
            name, wff = r
            try:
                lm, rm = self.parser.parse(wff)
                if rm.strip() != '':
                    print("[WARNING] Ignoring remainder:", r)
            except wffparser.Expects as e:
                print("[  ERROR]", e)
                return
            s = util.solve([self.find(n) for n in nms], lm)
            if s:
                print(s)
                self.locals[name] = lm
            else:
                print("[  ERROR] Unable to proceed.")
        elif line == "Show":
            print("Current State:", STATES[self.state])
            if self.state == GOAL:
                print("Goal", self.goalname, ":", logic.pretty(self.goal))
            print("Declared Predicates:", *self.parser.predicates)
            print("Declared Functions:", *self.parser.functions)
            print("Local names:")
            for name in self.locals:
                print(" ", name, logic.pretty(self.locals[name]))
            print("Global names:")
            for name in self.globals:
                print(" ", name, logic.pretty(self.globals[name]))
        elif line == "Abort":
            self.state = IDLE
            self.goal = None
            self.goalname = None
        else:
            print("[  ERROR] Unknown Command.")

    def find(self, name):
        if name in self.locals:
            return self.locals[name]
        elif name in self.globals:
            return self.globals[name]
        raise KeyError("Unknown identifier:", name)

    def loop(self):
        while True:
            self.read(input(" > "))

if __name__ == "__main__":
    r = REPL()
    r.loop()
