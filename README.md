# easyMathSolver

Mathematical expression parsing and solving with custom LaTeX grammar and interactive Jupyter widgets.

## Features

✅ **Automatic Building** - Parser builds automatically on first import
✅ **Cross-Platform Widgets** - Works in VS Code, JupyterLab, and Classic Notebook
✅ **MathLive Integration** - Interactive math editor with proper LaTeX encapsulation
✅ **Package-Name Agnostic** - Rename the package and everything still works
✅ **SymPy Integration** - Seamlessly patches SymPy's `parse_latex()`

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from easyMathSolver.main.manager import FormulaManager

# Create formula storage
math_storage = FormulaManager()

# Parse LaTeX (uses custom grammar automatically)
formula = math_storage.get("my_formula")
formula.fromLatex(r"E = m c^2")

# Display as LaTeX
print(formula.toLatex())  # Output: E = m c^{2}

# Get SymPy expression
expr = formula.toSympy()
print(expr)  # Output: Eq(E, c**2*m)
```

### Interactive Editor (Jupyter)

```python
# Create interactive MathLive editor
widget = formula.editor()
widget  # Display in Jupyter

# Changes in the editor automatically update formula.expr
```

## Architecture

### Custom LaTeX Parser

The package uses a custom `LaTeX.g4` ANTLR grammar file instead of SymPy's default parser:

```
latex_parser/
├── LaTeX.g4              # Your custom ANTLR grammar
├── __init__.py           # Auto-builder and SymPy patcher
├── _antlr/               # Generated parser (auto-created)
└── _build_custom_latex_parser.py
```

**How it works:**
1. On import, checks if parser is built
2. If not, auto-installs `antlr4-tools` and builds from `LaTeX.g4`
3. Patches `sympy.parsing.latex._antlr` to use custom parser
4. All `parse_latex()` calls now use your grammar

See [CUSTOM_PARSER_SETUP.md](CUSTOM_PARSER_SETUP.md) for details.

### MathLive Integration

Interactive math editor with automatic LaTeX encapsulation:

```python
formula.fromLatex(r"w_{nm}(E, E_0)")
latex = formula.toLatex()
# Output: w_{nm}{\left(E,E_{0} \right)}
# All subscripts/superscripts properly braced for MathLive
```

See [jupyter/README_MATHLIVE.md](jupyter/README_MATHLIVE.md) for details.

## Components

### FormulaManager

Storage and management of multiple formulas:

```python
math_storage = FormulaManager()

# Add formulas
math_storage.add("energy").fromLatex(r"E = m c^2")
math_storage.add("pythagorean").fromLatex(r"a^2 + b^2 = c^2")

# Access formulas
energy = math_storage.get("energy")

# Save/load
math_storage.save("formulas.json")
math_storage.load("formulas.json")
```

### FormulaParser

Individual formula parsing and conversion:

```python
from easyMathSolver.jupyter.formulas import FormulaParser

parser = FormulaParser()

# LaTeX ↔ SymPy
parser.fromLatex(r"\frac{a}{b}")
expr = parser.toSympy()
latex = parser.toLatex()

# Substitution
parser.subs({'a': 2, 'b': 3})

# Interactive editor
widget = parser.editor()
```

## Widget Support

### anywidget (Recommended)

Works in **all** Jupyter environments:

```python
# Install
pip install anywidget traitlets

# Use
widget = formula.editor()
# Works in: VS Code, JupyterLab, Classic Notebook, Colab
```

### ipywidgets (Fallback)

Standard Jupyter widgets:

```python
# Install
pip install ipywidgets

# Automatically used if anywidget not available
```

## Customization

### Modify LaTeX Grammar

1. Edit `latex_parser/LaTeX.g4`
2. Delete `latex_parser/_antlr/`
3. Restart Python - parser auto-rebuilds

### Add Custom Symbol Names

```python
class MyFormulaParser(FormulaParser):
    symbol_names = {'rho': r'\rho', 'alpha': r'\alpha'}
```

## Examples

### Example 1: Energy Formula

```python
formula = FormulaParser()
formula.fromLatex(r"E = \frac{1}{2} m v^2")

# Substitute values
formula.subs({'m': 2, 'v': 10})
result = formula.toSympy()
print(result)  # Eq(E, 100)
```

### Example 2: Interactive Equation Editor

```python
math_storage = FormulaManager()
eqn = math_storage.get("wave_equation")

# Show editor
widget = eqn.editor()
widget  # User can edit the equation interactively

# Access updated expression
print(eqn.toSympy())
```

### Example 3: Batch Processing

```python
formulas = {
    "kinetic": r"KE = \frac{1}{2} m v^2",
    "potential": r"PE = m g h",
    "total": r"E = KE + PE"
}

storage = FormulaManager()
for name, latex in formulas.items():
    storage.add(name).fromLatex(latex)

storage.save("physics.json")
```

## Documentation

- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [CUSTOM_PARSER_SETUP.md](CUSTOM_PARSER_SETUP.md) - Custom parser setup
- [jupyter/README_MATHLIVE.md](jupyter/README_MATHLIVE.md) - MathLive integration
- [latex_parser/README.md](latex_parser/README.md) - Parser internals

## Requirements

See `requirements.txt`, `requirements-minimal.txt`, and `requirements-dev.txt`.

**Core:**
- sympy >= 1.12
- bidict >= 0.22.0
- dotmap >= 1.3.30

**Jupyter (Optional):**
- anywidget >= 0.9.0 (recommended)
- ipywidgets >= 8.0.0 (fallback)
- ipython >= 8.0.0

**Parser Building:**
- antlr4-tools (auto-installed)
- antlr4-python3-runtime >= 4.13.0

## Platform Support

| Platform | Widget Support | Custom Parser |
|----------|---------------|---------------|
| VS Code | ✅ anywidget | ✅ |
| JupyterLab | ✅ anywidget, ipywidgets | ✅ |
| Jupyter Notebook (Classic) | ✅ anywidget, ipywidgets | ✅ |
| Jupyter Notebook v7+ | ✅ anywidget, ipywidgets | ✅ |
| Google Colab | ✅ anywidget | ✅ |
| Python Script | ❌ N/A | ✅ |

## License

MIT License

Copyright (c) 2024 David Ziegler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

**Contributions by:** David Ziegler ([techblogio.com](https://techblogio.com))

Contributions are welcome! Please feel free to submit a Pull Request.

## Version

1.0.0
