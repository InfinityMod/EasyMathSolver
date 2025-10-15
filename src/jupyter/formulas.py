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


# ============================================================================
# SHARED CONFIGURATION FOR MATHLIVE EDITOR
# ============================================================================

# Shared CSS for both anywidget and HTML implementations
MATHLIVE_CSS = """
    .mathfield-container {
        overflow: visible !important;
        position: relative;
        width: 100%;
        margin-bottom: 1em;
    }
    .mathfield-container.keyboard-visible {
        min-height: 400px;
    }
    math-field {
        display: block;
        padding: 0.5em;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1.728em;
        overflow: visible !important;
        min-height: 2em;
        width: 100%;
    }
    /* Position keyboard INSIDE container, not at page bottom */
    .mathfield-container .ML__keyboard,
    .mathfield-container math-virtual-keyboard {
        position: absolute !important;
        top: 100% !important;
        left: 0 !important;
        right: 0 !important;
        bottom: auto !important;
        z-index: 1000 !important;
        margin-top: 0.5em !important;
    }
    /* Force parent containers to expand and be visible */
    .jp-OutputArea-output,
    .jp-RenderedHTMLCommon,
    .jp-OutputArea-child,
    .output_subarea,
    .widget-subarea {
        overflow: visible !important;
        min-height: inherit;
    }
    /* Ensure widget output area expands */
    .jupyter-widgets-view {
        overflow: visible !important;
        min-height: inherit;
    }
"""

# Shared JavaScript for keyboard management logic
KEYBOARD_LOGIC_JS = """
    // Track keyboard visibility and expand container
    let keyboardVisible = false;

    function showKeyboard() {
        container.classList.add('keyboard-visible');
        keyboardVisible = true;
        keyboardBtn.textContent = '⌨️ Hide Keyboard';
    }

    function hideKeyboard() {
        container.classList.remove('keyboard-visible');
        keyboardVisible = false;
        keyboardBtn.textContent = '⌨️ Keyboard';
    }

    // Button click to toggle keyboard by focusing/blurring
    keyboardBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (keyboardVisible) {
            mf.blur();
            hideKeyboard();
        } else {
            mf.focus();
            showKeyboard();
        }
    });

    mf.addEventListener('focus', () => {
        // Expand container when field gets focus (keyboard will appear with auto policy)
        setTimeout(() => {
            showKeyboard();
            // Move keyboard into container if it exists
            const kbd = document.querySelector('math-virtual-keyboard');
            if (kbd && !container.contains(kbd)) {
                container.appendChild(kbd);
            }
        }, 100);
    });

    mf.addEventListener('blur', () => {
        // Collapse container when field loses focus
        setTimeout(() => {
            if (!mf.hasFocus()) {
                hideKeyboard();
            }
        }, 200);
    });
"""

# ============================================================================
# ANYWIDGET IMPLEMENTATION
# ============================================================================

if ANYWIDGET_AVAILABLE:
    class MathFieldWidget(anywidget.AnyWidget):
        """MathLive formula editor widget (works in VS Code, JupyterLab, Classic Notebook)"""
        value = traitlets.Unicode('').tag(sync=True)
        _esm = f"""
        async function render({{ model, el }}) {{
            // Load MathLive (latest version via official ESM CDN)
            if (!window.MathfieldElement) {{
                await import('https://esm.run/mathlive');

                // Add custom styles
                const style = document.createElement('style');
                style.innerHTML = `{MATHLIVE_CSS}`;
                document.head.appendChild(style);
            }}

            // Create container with label and keyboard button
            const container = document.createElement('div');
            container.className = 'mathfield-container';

            const labelContainer = document.createElement('div');
            labelContainer.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5em;';

            const label = document.createElement('label');
            label.textContent = 'Math-Editor';
            labelContainer.appendChild(label);

            const keyboardBtn = document.createElement('button');
            keyboardBtn.textContent = '⌨️ Keyboard';
            keyboardBtn.style.cssText = 'padding: 0.25em 0.5em; font-size: 0.9em; cursor: pointer;';
            labelContainer.appendChild(keyboardBtn);

            container.appendChild(labelContainer);

            const mf = document.createElement('math-field');
            mf.value = model.get('value');
            container.appendChild(mf);

            el.appendChild(container);

            await customElements.whenDefined('math-field');

            // Set MathLive properties
            mf.smartFence = true;
            mf.removeExtraneousParentheses = true;
            mf.mathVirtualKeyboardPolicy = "auto";  // Auto-show keyboard on focus

            {KEYBOARD_LOGIC_JS}

            mf.addEventListener('input', () => {{
                model.set('value', mf.value);
                model.save_changes();
            }});

            model.on('change:value', () => {{
                if (mf.value !== model.get('value')) mf.value = model.get('value');
            }});
        }}
        export default {{ render }};
        """

        def __init__(self, initial_latex='', **kwargs):
            super().__init__(**kwargs)
            self.value = initial_latex


# ============================================================================
# FORMULA PARSER CLASS
# ============================================================================

class FormulaParser:
    # Map symbol names to their LaTeX representations
    # This includes Greek letters to ensure proper rendering
    symbol_names = {
        'rho': r'\rho',
        # Lowercase Greek letters
        'alpha': r'\alpha', 'beta': r'\beta', 'gamma': r'\gamma', 'delta': r'\delta',
        'epsilon': r'\epsilon', 'zeta': r'\zeta', 'eta': r'\eta', 'theta': r'\theta',
        'iota': r'\iota', 'kappa': r'\kappa', 'lambda': r'\lambda', 'mu': r'\mu',
        'nu': r'\nu', 'xi': r'\xi', 'omicron': r'\omicron', 'pi': r'\pi',
        'rho': r'\rho', 'sigma': r'\sigma', 'tau': r'\tau', 'upsilon': r'\upsilon',
        'phi': r'\phi', 'chi': r'\chi', 'psi': r'\psi', 'omega': r'\omega',
        # Uppercase Greek letters
        'Alpha': r'\Alpha', 'Beta': r'\Beta', 'Gamma': r'\Gamma', 'Delta': r'\Delta',
        'Epsilon': r'\Epsilon', 'Zeta': r'\Zeta', 'Eta': r'\Eta', 'Theta': r'\Theta',
        'Iota': r'\Iota', 'Kappa': r'\Kappa', 'Lambda': r'\Lambda', 'Mu': r'\Mu',
        'Nu': r'\Nu', 'Xi': r'\Xi', 'Omicron': r'\Omicron', 'Pi': r'\Pi',
        'Rho': r'\Rho', 'Sigma': r'\Sigma', 'Tau': r'\Tau', 'Upsilon': r'\Upsilon',
        'Phi': r'\Phi', 'Chi': r'\Chi', 'Psi': r'\Psi', 'Omega': r'\Omega',
    }

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

    def _fix_exponential_parsing_bug(self, latx):
        r"""
        Fix SymPy LaTeX parser bug where e^{-\frac{...}{...}} after \cdot is
        incorrectly parsed as division instead of multiplication.

        Converts patterns like:
        - e^{-\frac{A}{B}} → \exp(-\frac{A}{B})
        - e^{-(...)} → \exp(-(...))

        This ensures proper parsing when exponentials appear after \cdot.
        """
        import re

        # Pattern 1: e^{- followed by \frac{...}{...} and closing brace
        # This is the most problematic pattern
        def replace_efrac(match):
            content = match.group(1)
            return f'\\exp(-{content})'

        # Match: e^{-\frac{...}{...}}
        # We need to match balanced braces
        latx = re.sub(
            r'e\^\{-\\frac\{([^}]+)\}\{([^}]+)\}\}',
            lambda m: f'\\exp(-\\frac{{{m.group(1)}}}{{{m.group(2)}}})',
            latx
        )

        # Pattern 2: e^{-(...)} where parentheses contain the expression
        latx = re.sub(
            r'e\^\{-\(([^)]+)\)\}',
            lambda m: f'\\exp(-({m.group(1)}))',
            latx
        )

        return latx

    def _protect_mixed_subscripts(self, latx):
        r"""
        Protect multi-character subscripts from being parsed as multiplication.

        The SymPy parser treats subscripts like _{rear} as r*e*a*r and _{n12m} as n*12*m.
        We wrap them in \mathit{} to preserve them as a single unit.

        Converts:
            _{rear} → _{\mathit{rear}}
            _{n12m} → _{\mathit{n12m}}

        Single-character subscripts are left as-is: _{r} → _{r}
        """
        import re

        def protect_subscript(match):
            r"""Wrap multi-character subscripts in \mathit{}"""
            content = match.group(1)

            # Check if content has multiple alphanumeric characters
            # (excluding LaTeX commands which start with \)
            if not content.startswith('\\'):
                # Count alphanumeric characters
                alphanum_chars = re.findall(r'[a-zA-Z0-9]', content)

                # If more than one alphanumeric character, protect it
                if len(alphanum_chars) > 1:
                    return '_\\mathit{' + content + '}'

            # Keep as-is for single characters or LaTeX commands
            return match.group(0)

        # Match subscripts: _{...}
        # But exclude those already wrapped in \text, \mathit, etc.
        latx = re.sub(r'_\{(?!\\text|\\mathit|\\mathrm)([^}]+)\}', protect_subscript, latx)

        return latx

    def _fix_comma_in_subscripts(self, latx):
        r"""
        Fix SymPy LaTeX parser bug where commas in subscripts cause parsing errors.

        The parser treats commas as function argument separators, which breaks
        subscripts like r_{sum,j}.

        Converts: r_{sum,j} → r_{sumj} (removes comma)
        Note: This is a workaround - the comma cannot be preserved due to parser limitations.
        """
        import re

        def replace_comma_in_subscript(match):
            """Remove comma from subscript"""
            content = match.group(1)
            # Simply remove the comma and any spaces around it
            return '_{' + content.replace(',', '').replace(' ', '') + '}'

        # Match subscripts with commas: _{...,...}
        latx = re.sub(r'_\{([^}]*,[^}]*)\}', replace_comma_in_subscript, latx)

        return latx

    def cleanLatex(self, latx):
        latx = latx.replace(r'\exponentialE', 'e')
        latx = latx.replace(r'\differentialD', r'd')
        latx = self._protect_mixed_subscripts(latx)
        latx = self._fix_comma_in_subscripts(latx)
        latx = self._fix_exponential_parsing_bug(latx)
        return latx

    def fromLatex(self, latx):
        latx = self.cleanLatex(latx)
        self._lt = latx
        self.setExpr(parse_latex(latx))
        return self

    def toLatex(self):
        """Convert expression to LaTeX with proper encapsulation for MathLive"""
        latex = sympy.latex(self.expr, symbol_names=self.symbol_names)
        latex = self._fix_greek_letters(latex)
        latex = self._make_multiplication_explicit(latex)
        return self._encapsulate_for_mathlive(latex)

    def _fix_greek_letters(self, latex):
        """
        Fix Greek letter symbols that appear without backslash.

        When SymPy parses symbols like Beta_{r}, it creates a symbol with name "Beta_{r}"
        and latex() outputs "Beta_{r}" instead of "\\Beta_{r}".

        This method adds the backslash to Greek letter names.
        """
        import re

        # List of Greek letter names (both cases)
        greek_letters = [
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
            'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi',
            'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
            'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta',
            'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi',
            'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
        ]

        for greek in greek_letters:
            # Match Greek letter name that's NOT preceded by backslash
            # Must be at word start (space, start of string, or after operator)
            pattern = r'(?<!\\)(?<![a-zA-Z])' + greek + r'(?![a-zA-Z])'
            replacement = r'\\' + greek
            latex = re.sub(pattern, replacement, latex)

        return latex

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

        def encapsulate_script(match):
            """Encapsulate the subscript or superscript"""
            operator = match.group(1)  # _ or ^
            content = match.group(2)   # The content after _ or ^

            # If already braced, return as-is
            if content.startswith('{'):
                return match.group(0)

            # If single char/digit followed by space or operator, leave as-is
            if len(content) == 1:
                return match.group(0)

            # Multiple characters without braces - encapsulate
            return f"{operator}{{{content}}}"

        # Pattern: ([_^])(?!\{)([a-zA-Z0-9]+)(?![}])
        latex = re.sub(r'([_^])(?!\{)([a-zA-Z0-9]+)(?![}])', encapsulate_script, latex)

        # Handle edge case: _{} or ^{} followed by non-braced content
        def merge_adjacent_scripts(match):
            """Merge adjacent subscripts or superscripts"""
            operator = match.group(1)
            braced = match.group(2)
            following = match.group(3)
            return f"{operator}{{{braced[1:-1]}{following}}}"

        latex = re.sub(r'([_^])(\{[^}]+\})([a-zA-Z0-9]+)', merge_adjacent_scripts, latex)

        return latex

    def _make_multiplication_explicit(self, latex):
        r"""
        Convert implicit multiplications (spaces between components) to explicit \cdot in LaTeX.

        Important: Only spaces between distinct components are treated as multiplication.
        Multi-letter variables without spaces (like 'abc') remain as single components.

        Patterns fixed:
        1. number + space + variable (e.g., "0.5 x" -> "0.5 \cdot x")
        2. closing brace + space + variable (e.g., "e^{x} y" -> "e^{x} \cdot y")
        3. closing brace + space + LaTeX command (e.g., "E_{0} \beta" -> "E_{0} \cdot \beta")
        4. LaTeX command + space + variable (e.g., "\beta E_0" -> "\beta \cdot E_0")
        5. \right) + space + \left( (e.g., "\right) \left(" -> "\right) \cdot \left(")
        6. single letter + space + single letter (e.g., "E E_0" -> "E \cdot E_0")
           BUT NOT consecutive letters without space (e.g., "abc" stays as "abc")

        Examples of what is preserved:
        - "abc" stays as "abc" (no spaces = single component)
        - "gamma" stays as "gamma" (part of \gamma command)
        - "mathit{nm}" stays intact (inside braces)
        """
        import re

        # Use a placeholder to avoid double-matching
        PLACEHOLDER = '<<<CDOT>>>'

        # Pattern 1: number (possibly decimal) + space + any letter or backslash (LaTeX command start)
        # Matches: "0.5 x", "123 y", "3.14159 r", "2 \beta"
        latex = re.sub(
            r'(\d+\.?\d*)\s+([a-zA-Z\\])',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Pattern 2: closing brace } + space + single letter (not followed by more letters)
        # Matches: "e^{x} y", "_{0}} E"
        # Does NOT match: "} abc" where abc is a multi-letter variable
        latex = re.sub(
            r'(\})\s+([a-zA-Z])(?![a-zA-Z])',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Pattern 3: closing brace } + space + LaTeX command (starts with \)
        # Matches: "E_{0} \beta", "x^{2} \alpha"
        # EXCLUDES: \left and \right (these are delimiters, not operators)
        latex = re.sub(
            r'(\})\s+(\\(?!left|right)[a-zA-Z]+)',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Pattern 4: LaTeX command + space + variable or number
        # Matches: "\beta E_0", "\alpha x", "\gamma 5"
        latex = re.sub(
            r'(\\[a-zA-Z]+)\s+([a-zA-Z0-9])',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Pattern 5: \right) + space + \left(
        # Matches: "\right) \left(" for adjacent parentheses
        latex = re.sub(
            r'(\\right\))\s+(\\left\()',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Pattern 6: single letter + space + single letter
        # Matches: "E E_0", "x y" (but NOT "abc" without space)
        # Must not be preceded by backslash (part of LaTeX command)
        # Must not be followed by more letters (multi-letter variable)
        latex = re.sub(
            r'(?<!\\)([a-zA-Z])(?![a-zA-Z_^])\s+([a-zA-Z])(?![a-zA-Z])',
            lambda m: f'{m.group(1)}{PLACEHOLDER}{m.group(2)}',
            latex
        )

        # Replace placeholder with actual \cdot
        latex = latex.replace(PLACEHOLDER, ' \\cdot ')

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
        return self._create_html_editor(initial_latex)

    def _create_html_editor(self, initial_latex):
        """Create HTML-based editor with MathLive for non-anywidget environments"""
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

        # Build HTML using shared CSS and JS
        html = f"""
        <style>{MATHLIVE_CSS}</style>
        <div class="mathfield-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5em;">
                <label>Math-Editor</label>
                <button id="kb_{identifier}" style="padding: 0.25em 0.5em; font-size: 0.9em; cursor: pointer;">⌨️ Keyboard</button>
            </div>
            <math-field id="mf_{identifier}" style="display: block; padding: 0.5em; border: 1px solid #ccc; border-radius: 4px; font-size: 1.728em; overflow: visible; min-height: 2em; width: 100%;">{initial_latex}</math-field>
        </div>
        <script type="module">
        (async () => {{
            // Load MathLive
            if (!window.MathfieldElement) {{
                await import('https://esm.run/mathlive');
            }}

            const mf = document.getElementById('mf_{identifier}');
            const container = mf.closest('.mathfield-container');
            const keyboardBtn = document.getElementById('kb_{identifier}');

            await customElements.whenDefined('math-field');

            // Set MathLive properties
            mf.smartFence = true;
            mf.removeExtraneousParentheses = true;
            mf.mathVirtualKeyboardPolicy = "auto";

            {KEYBOARD_LOGIC_JS}

            // Setup comm or kernel communication
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
