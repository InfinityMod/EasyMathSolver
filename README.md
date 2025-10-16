# easyMathSolver

## Mission

Making formulas editable in Python and easy to display, while integrating a full calculation framework (SymPy) with support to transform them to executables.

**This eases the work with difficult formulas.**

Mathematical expressions are often complex and hard to manage in code. easyMathSolver bridges the gap between interactive formula editing, symbolic computation, and executable code - all while maintaining full compatibility with SymPy's powerful mathematical engine.

## Features

- **Editing**: Interactive formula editor with live preview using MathLive
- **View**: Beautiful LaTeX rendering in Jupyter notebooks and export to various formats
- **Execution**: Direct evaluation with variable substitution and numerical computation
- **Insert**: Embed formulas or factors into existing expressions seamlessly
- **Full SymPy Support**: Complete integration with SymPy's symbolic mathematics capabilities
- **Multi-Formula Storage**: Manage collections of related formulas with the FormulaManager
- **Import/Export**: Save and load formulas as JSON for persistence and sharing
- **Live Synchronization**: Edits in the formula editor are directly reflected in the backend

## Example
https://github.com/user-attachments/assets/d6ade1ea-fc2b-4b4f-9b81-241828d19cff

## Architecture

### Frontend: MathLive Editor

The system provides two integration methods for interactive formula editing in Jupyter notebooks:

1. **Jupyter Widget (Recommended)**: Modern widget implementation using `anywidget` for cross-platform compatibility
   - Works in VS Code, JupyterLab, Classic Notebook, and Google Colab
   - Real-time bidirectional synchronization between editor and Python backend

2. **HTML Insert (Legacy)**: Direct HTML insertion for older environments
   - Fallback option for environments without widget support

Both methods use **MathLive**, a powerful JavaScript library that provides:
- Interactive mathematical keyboard
- LaTeX syntax support with visual editing
- Proper mathematical notation rendering

### Transformation Layer: LaTeX ↔ SymPy

The core of easyMathSolver is the transformation layer that maintains cross-compatibility between MathLive (LaTeX) and SymPy (symbolic expressions).

**Key Components:**

1. **Custom LaTeX Parser**: Enhanced ANTLR-based parser (`LaTeX.g4`) that extends SymPy's default LaTeX parsing
   - Auto-builds on first import
   - Seamlessly patches `sympy.parsing.latex._antlr`
   - Handles edge cases and special notations

2. **Adapted Parsing Logic**: Special preprocessing and postprocessing to ensure compatibility
   - Explicit multiplication handling (spaces → `\cdot`)
   - Greek letter normalization
   - Subscript and superscript protection
   - Exponential parsing bug fixes
   - Mixed alphanumeric subscript preservation

3. **LaTeX Encapsulation**: Automatic formatting for MathLive compatibility
   - Proper bracing of subscripts/superscripts
   - Delimiter handling (`\left`, `\right`)
   - Symbol name mapping

**Data Flow:**
```
User Input (MathLive) → LaTeX String → Parser → SymPy Expression → Computation
                          ↑                                            ↓
                          └────────── LaTeX Output ←──────────────────┘
```

### Backend: FormulaManager

The **FormulaManager** provides a centralized system for managing multiple formulas:

- **Storage**: Keep related formulas organized in collections
- **Persistence**: Save/load formula collections as JSON files
- **Access**: Quick retrieval by name or key
- **Batch Operations**: Process multiple formulas efficiently

Each formula is represented by a **FormulaParser** instance that handles:
- LaTeX to SymPy conversion
- Variable substitution
- Expression evaluation
- LaTeX rendering with proper formatting

## Examples

### Example 1: Interactive Formula Editing

```python
from easyMathSolver.main.manager import FormulaManager

# Create formula storage
math_storage = FormulaManager()

# Add a formula and edit interactively
energy = math_storage.add("energy")
energy.fromLatex(r"E = m c^2")

# Display interactive editor in Jupyter
widget = energy.editor()
widget  # User can now edit the formula visually

# Changes are immediately reflected
print(energy.toSympy())  # Shows updated expression
```

### Example 2: Variable Substitution and Execution

```python
from easyMathSolver.jupyter.formulas import FormulaParser

# Parse kinetic energy formula
formula = FormulaParser()
formula.fromLatex(r"KE = \frac{1}{2} m v^2")

# Substitute values
formula.subs({'m': 2, 'v': 10})
result = formula.toSympy()
print(result)  # Eq(KE, 100)

# Solve for a variable
print(formula.toSympy().rhs)  # 100
```

### Example 3: Inserting Formulas into Other Formulas

```python
# Create related formulas
storage = FormulaManager()

storage.add("kinetic").fromLatex(r"KE = \frac{1}{2} m v^2")
storage.add("potential").fromLatex(r"PE = m g h")

# Get SymPy expressions
ke = storage.get("kinetic").toSympy().rhs
pe = storage.get("potential").toSympy().rhs

# Combine into total energy formula
total = FormulaParser()
total.expr = ke + pe
print(total.toLatex())  # Shows combined formula
```

### Example 4: Multi-Formula Storage and Persistence

```python
# Create a collection of physics formulas
formulas = {
    "newton_second": r"F = m a",
    "work": r"W = F d",
    "power": r"P = \frac{W}{t}",
    "momentum": r"p = m v",
    "impulse": r"J = F \Delta t"
}

storage = FormulaManager()
for name, latex in formulas.items():
    storage.add(name).fromLatex(latex)

# Save to file
storage.save("physics_formulas.json")

# Load later
new_storage = FormulaManager()
new_storage.load("physics_formulas.json")

# Access formulas
force = new_storage.get("newton_second")
print(force.toLatex())
```

### Example 5: Complex Formula with Space-Based Multiplication

```python
# Handle formulas with implicit multiplication (spaces)
formula = FormulaParser()

# Input with spaces between components
formula.fromLatex(r"w_{nm}(E, E_0) = N \cdot (1 - e^{-\gamma \frac{E}{E_0}}) \cdot e^{-\frac{E}{\beta E_0}}")

# System automatically makes multiplications explicit
print(formula.toLatex())  # Properly formatted with \cdot

# Access as SymPy expression for computation
expr = formula.toSympy()
```

### Example 6: Greek Letters and Special Notation

```python
# Greek letters and complex subscripts
formula = FormulaParser()
formula.fromLatex(r"\Delta_r + \Beta_r = \alpha_{n12m} \cdot \gamma")

# Properly handles Greek letters and mixed alphanumeric subscripts
print(formula.toLatex())  # Correctly formatted
print(formula.toSympy())  # Symbolic expression
```

### Example 7: Batch Processing and Analysis

```python
# Process multiple formulas
storage = FormulaManager()

# Define electromagnetic formulas
em_formulas = {
    "coulomb": r"F = k \frac{q_1 q_2}{r^2}",
    "electric_field": r"E = \frac{F}{q}",
    "gauss": r"\Phi_E = \frac{Q}{\epsilon_0}",
    "capacitance": r"C = \frac{Q}{V}"
}

for name, latex in em_formulas.items():
    storage.add(name).fromLatex(latex)

# Export all formulas
storage.save("electromagnetic_formulas.json")

# Batch substitution
storage.get("coulomb").subs({'k': 8.99e9, 'q_1': 1e-6, 'q_2': 2e-6, 'r': 0.1})
result = storage.get("coulomb").toSympy()
print(f"Force: {result.rhs} N")
```

## Installation

```bash
pip install -r requirements.txt
```

**Core Requirements:**
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

### Areas for Contribution

- Additional LaTeX notation support
- Performance optimizations
- Extended SymPy integration features
- Documentation improvements
- Bug fixes and edge case handling
- Additional export formats
- Enhanced widget features

## Version

1.0.0
