import json
from dotmap import DotMap
from easyMathSolver.jupyter.formulas import FormulaParser

# Custom LaTeX parser is automatically loaded via easyMathSolver.__init__


class FormulaManager(DotMap):

    def __init__(self, *args, **kwargs):
        super().__init__(_dynamic=False)

    def add(self, name):
        self[name] = FormulaParser()
        return self[name]

    def get(self, name):
        if name not in self:
            self[name] = FormulaParser()
        return self[name]

    def remove(self, name):
        del self[name]
        return self

    def load(self, path):
        with open(path, "r") as f:
            self.clear()
            for n, v in json.load(f).items():
                self[n] = FormulaParser().load(v)
        return self

    def save(self, path):
        with open(path, "w") as f:
            f.write(json.dumps({n: v.export() for n, v in self.items()}))
        return self

    def cleanEmpty(self):
        for name, formula in list(self.items()):
            if formula.isEmpty():
                self.items.pop(name)
        return self

    @staticmethod
    def latexSymbol(expr):
        return FormulaParser().fromLatex(expr).toSympy()


if __name__ == "__main__":
    import os
    fm = FormulaManager()
    fm.add("Test").fromLatex("x^n + y^n = z^n")
    fm.save("Test.json")
    fm.load("Test.json")
    os.remove("Test.json")
