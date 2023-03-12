import sympy
import random
import string
import time
from bidict import bidict
from sympy import sympify, Symbol
from sympy.parsing.latex import parse_latex
from sympy.printing.latex import latex_escape
from sympy.parsing.sympy_parser import parse_expr
from IPython.display import HTML, Javascript, display


class FormulaParser:
    symbol_names = {'rho': r'\rho'}

    def __init__(self):
        self.expr = None
        self._lt = None
        self.sym_dct = bidict()
        self.iter = self.expr_subs()
        self.mathfield_initialized = False
        self.mathfield_identifier = None

    def _initialize_mathfield_jupyter(self, globals=globals()):
        _html = """
            <script type="module">
                if (window.mathlive == undefined){
                    import('https://unpkg.com/mathlive?module').then((mathlive) => {
                        // Create Keyboard
                        mathlive.makeSharedVirtualKeyboard({
                          virtualKeyboardLayout: 'dvorak',
                        });
                        window.mathlive = mathlive;
                        IPython.notebook.kernel.execute("matlive_loaded=True");
                    });

                    var link = document.createElement('link');
                    link.type = 'text/css';
                    link.rel = 'stylesheet';
                    link.href = 'https://unpkg.com/mathlive/dist/mathlive-static.css';
                    document.head.appendChild(link);

                    var style = document.createElement('style')
                    style.innerHTML = " \
                        .formula{ \
                            font-size: 1.728em \
                         } \
                    "
                    document.head.appendChild(style);
                }
            </script>
        """
        display(HTML(_html))
        if self.mathfield_identifier is None:
            while self.mathfield_identifier is None or self.mathfield_identifier in globals:
                self.mathfield_identifier = "cb_" + ''.join(random.sample(string.ascii_lowercase, 8))
        globals[self.mathfield_identifier] = lambda x, _self=self: _self.fromLatex(x)
        self.mathfield_initialized = True

    def expr_subs(self, start="a", stop="z", step=1, ntimes=True):
        """Yield a range of lowercase letters."""
        level = 0
        prefix = ""
        while True:
            if level > 0 and ntimes:
                for prefix in self.expr_subs():
                    for ord_ in range(ord(start.lower()), ord(stop.lower()) + 1, step):
                        yield prefix + chr(ord_)
            else:
                for ord_ in range(ord(start.lower()), ord(stop.lower()) + 1, step):
                    yield prefix + chr(ord_)
            level += 1

    def setExpr(self, expr):
        self.expr = expr
        if self.mathfield_initialized:
            _html = "document.getElementById('formula_{0}')\
                        .setValue(ev.target.value,{{suppressChangeNotifications: true}});".format(self.mathfield_identifier)
            display(HTML(_html))

    def cleanLatex(self, latx):
        latx = latx.replace("\exponentialE", "e")
        latx = latx.replace("\differentialD", "\d")
        return latx

    def fromLatex(self, latx):
        latx = self.cleanLatex(latx)
        self._lt = latx
        self.setExpr(parse_latex(latx))
        return self

    def toLatex(self):
        return sympy.latex(self.expr, symbol_names=self.symbol_names)

    def toSage(self):
        expr = self.expr
        for a in expr.atoms(Symbol):
            self.sym_dct[a] = Symbol(next(self.iter))
            expr = expr.subs(a, self.sym_dct[a])
        return expr._sage_()

    def fromSage(self, sage):
        expr = sage._sympy_()
        for a in expr.atoms(Symbol):
            expr = expr.subs(a, self.sym_dct.inv[a])
        self.setExpr(self.expr)
        return self

    def toSympy(self):
        return self.expr

    def fromSympy(self, expr):
        self.setExpr(expr)
        return self

    def editor(self, globals=globals()):
        self._initialize_mathfield_jupyter(globals=globals)
        _html = """
        <label>Math-Editor</label>
        <math-field use-shared-virtual-keyboard id="formula_{0}" class="formula">
            {1}
        </math-field>
        <script type="module">
            function _render_matlive(){{
                if(window.mathlive){{
                    console.log("Matlive observer {0} started!")
                    mathlive.renderMathInDocument()
                    var mf = document.getElementById('formula_{0}');
                    mf.addEventListener('input',(ev) => {{
                        IPython.notebook.kernel.execute("{0}(r'"+mf.value+"')");
                    }});     
                    mf.setOptions({{
                        virtualKeyboardMode: "manual",
                        virtualKeyboards: "",
                        smartFence: false,
                        removeExtraneousParentheses: true
                    }});
                }}else{{
                    setTimeout(function(){{_render_matlive()}},100);
                }}
            }}
            _render_matlive();
         </script>
        """.format(self.mathfield_identifier, self.toLatex())
        display(HTML(_html))

    def isEmpty(self):
        return self.expr == None

    def load(self, obj):
        self.sym_dct = bidict(obj["sym_dct"])
        self._lt = obj["lt"]
        if self._lt is not None:
            self.fromLatex(obj["lt"])
        return self

    def export(self):
        return {"expr": str(self.expr), "sym_dct": dict(self.sym_dct), "lt": self._lt}

    def _repr_latex_(self):
        try:
            return '$ {\large ' + self.toLatex() + '}$'
        except AttributeError:
            return None    # if None is returned, plain text is used
