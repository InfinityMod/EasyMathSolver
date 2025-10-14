import sympy
import random
import string
from bidict import bidict
from sympy import sympify, Symbol
from sympy.printing.latex import latex_escape
from sympy.parsing.sympy_parser import parse_expr
from IPython.display import HTML, display

# Ensure custom parser is loaded (imports package __init__ which triggers parser setup)
from .. import __package_name__  # This triggers the custom parser setup via __init__.py
from sympy.parsing.latex import parse_latex

# Try anywidget first (best compatibility), then fallback to ipywidgets
try:
    import anywidget
    import traitlets
    ANYWIDGET_AVAILABLE = True
except ImportError:
    ANYWIDGET_AVAILABLE = False
    try:
        from ipywidgets import HTML as HTMLWidget
        IPYWIDGETS_AVAILABLE = True
    except ImportError:
        IPYWIDGETS_AVAILABLE = False


if ANYWIDGET_AVAILABLE:
    class MathFieldWidget(anywidget.AnyWidget):
        """MathLive formula editor widget (works in VS Code, JupyterLab, Classic Notebook)"""
        value = traitlets.Unicode('').tag(sync=True)

        _esm = """
        async function render({ model, el }) {
            // Load MathLive (latest version)
            if (!window.mathlive) {
                const ml = await import('https://unpkg.com/mathlive/dist/mathlive.mjs');
                ml.makeSharedVirtualKeyboard({ virtualKeyboardLayout: 'dvorak' });
                window.mathlive = ml;

                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://unpkg.com/mathlive/dist/mathlive-static.css';
                document.head.appendChild(link);

                const style = document.createElement('style');
                style.innerHTML = '.formula { font-size: 1.728em; }';
                document.head.appendChild(style);
            }

            const label = document.createElement('label');
            label.textContent = 'Math-Editor';
            el.appendChild(label);

            const mf = document.createElement('math-field');
            mf.setAttribute('use-shared-virtual-keyboard', '');
            mf.setAttribute('class', 'formula');
            mf.value = model.get('value');
            el.appendChild(mf);

            await customElements.whenDefined('math-field');

            // Set properties directly (modern MathLive API)
            mf.virtualKeyboardMode = "manual";
            mf.virtualKeyboards = "";
            mf.smartFence = false;
            mf.removeExtraneousParentheses = true;

            mf.addEventListener('input', () => {
                model.set('value', mf.value);
                model.save_changes();
            });

            model.on('change:value', () => {
                if (mf.value !== model.get('value')) mf.value = model.get('value');
            });
        }
        export default { render };
        """

        def __init__(self, initial_latex='', **kwargs):
            super().__init__(**kwargs)
            self.value = initial_latex
            display(initial_latex)


class FormulaParser:
    symbol_names = {'rho': r'\rho'}

    def __init__(self):
        self.expr = None
        self._lt = None
        self.sym_dct = bidict()
        self.iter = self.expr_subs()
        self._widget = None

    def _handle_latex_update(self, latex_value):
        """Common handler for LaTeX updates"""
        if latex_value:
            try:
                self.fromLatex(latex_value)
            except Exception as e:
                print(f"Error parsing LaTeX: {e}")

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
        self._lt = self.toLatex()

    def cleanLatex(self, latx):
        latx = latx.replace(r'\exponentialE', 'e')
        latx = latx.replace(r'\differentialD', r'd')
        return latx

    def fromLatex(self, latx):
        latx = self.cleanLatex(latx)
        self._lt = latx
        self.setExpr(parse_latex(latx))
        return self

    def toLatex(self):
        """Convert expression to LaTeX with proper encapsulation for MathLive"""
        latex = sympy.latex(self.expr, symbol_names=self.symbol_names)
        return self._encapsulate_for_mathlive(latex)

    def _encapsulate_for_mathlive(self, latex):
        """
        Encapsulate subscripts and superscripts with braces for MathLive compatibility.

        MathLive requires subscripts and superscripts to be encapsulated in braces
        when they contain more than one character to avoid parsing errors.

        Examples:
            x_nm -> x_{nm}
            x^2y -> x^{2}y  (if not already braced)
            x_{already} -> x_{already}  (unchanged)
        """
        import re

        # Pattern to find subscripts/superscripts that aren't already properly braced
        # Matches: _x or ^x where x is a single char not followed by {
        # or _xyz or ^xyz where xyz is multiple chars not wrapped in {}

        def encapsulate_script(match):
            """Encapsulate the subscript or superscript"""
            operator = match.group(1)  # _ or ^
            content = match.group(2)   # The content after _ or ^

            # If already braced, return as-is
            if content.startswith('{'):
                return match.group(0)

            # If it's a single character or digit, check if followed by another char
            # If single char/digit followed by space or operator, leave as-is
            if len(content) == 1:
                return match.group(0)

            # Multiple characters without braces - encapsulate
            return f"{operator}{{{content}}}"

        # Pattern explanation:
        # ([_^])           - Capture _ or ^
        # (?!{)            - Not followed by {
        # ([a-zA-Z0-9]+)   - Capture one or more alphanumeric chars
        # (?![}])          - Not followed by }
        latex = re.sub(r'([_^])(?!\{)([a-zA-Z0-9]+)(?![}])', encapsulate_script, latex)

        # Also handle case where there's a single char followed by more content
        # e.g., x_a_b should become x_{a}_{b}, but this is handled by above

        # Handle edge case: _{} or ^{} followed by non-braced content
        # e.g., x_{n}m should be x_{nm}
        def merge_adjacent_scripts(match):
            """Merge adjacent subscripts or superscripts"""
            operator = match.group(1)
            braced = match.group(2)
            following = match.group(3)
            return f"{operator}{{{braced[1:-1]}{following}}}"

        # Pattern: _{ content }following_chars
        latex = re.sub(r'([_^])(\{[^}]+\})([a-zA-Z0-9]+)', merge_adjacent_scripts, latex)

        return latex

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

    def editor(self):
        """Create an interactive math editor"""
        initial_latex = self.toLatex() if self.expr is not None else ''

        # Use anywidget (best compatibility: VS Code, JupyterLab, Classic Notebook)
        if ANYWIDGET_AVAILABLE:
            widget = MathFieldWidget(initial_latex=initial_latex)
            widget.observe(lambda c: self._handle_latex_update(c['new']), names='value')
            self._widget = widget
            return widget

        # Fallback to HTML with comm
        identifier = "cb_" + ''.join(random.sample(string.ascii_lowercase, 8))
        comm_target = f"mathfield_{identifier}"

        # Register comm handler
        try:
            def comm_handler(comm, msg):
                @comm.on_msg
                def _recv(msg):
                    self._handle_latex_update(msg['content']['data'].get('latex', ''))
            get_ipython().kernel.comm_manager.register_target(comm_target, comm_handler)
        except Exception:
            # Fallback: register in IPython user namespace
            try:
                get_ipython().user_ns[identifier] = lambda x, _self=self: _self._handle_latex_update(x)
            except:
                pass  # If all else fails, editor will be view-only

        # Concise HTML with MathLive (latest version)
        html = f"""
        <link rel="stylesheet" href="https://unpkg.com/mathlive/dist/mathlive-static.css">
        <style>.formula {{ font-size: 1.728em; }}</style>
        <label>Math-Editor</label>
        <math-field id="mf_{identifier}" class="formula" use-shared-virtual-keyboard>{initial_latex}</math-field>
        <script type="module">
        (async () => {{
            if (!window.mathlive) {{
                const ml = await import('https://unpkg.com/mathlive/dist/mathlive.mjs');
                ml.makeSharedVirtualKeyboard({{ virtualKeyboardLayout: 'dvorak' }});
                window.mathlive = ml;
            }}
            const mf = document.getElementById('mf_{identifier}');

            // Set properties directly (modern MathLive API)
            mf.virtualKeyboardMode = "manual";
            mf.virtualKeyboards = "";
            mf.smartFence = false;
            mf.removeExtraneousParentheses = true;

            const k = (typeof IPython !== 'undefined' && IPython?.notebook?.kernel) || (typeof Jupyter !== 'undefined' && Jupyter?.notebook?.kernel);
            if (k?.comm_manager) {{
                const c = k.comm_manager.new_comm('{comm_target}');
                mf.addEventListener('input', () => c.send({{ latex: mf.value }}));
            }} else if (k) {{
                mf.addEventListener('input', () => k.execute(`{identifier}(r'${{mf.value}}')`));
            }}
        }})();
        </script>
        """

        if IPYWIDGETS_AVAILABLE:
            widget = HTMLWidget(value=html)
            self._widget = widget
            return widget
        else:
            display(HTML(html))

    def subs(self, dct: dict):
        for n, v in dct.items():
            self.expr = self.expr.subs(n, v)
        self.setExpr(self.expr)
        return self

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
            return r'$ {\large ' + self.toLatex() + r'}$'
        except AttributeError:
            return None
