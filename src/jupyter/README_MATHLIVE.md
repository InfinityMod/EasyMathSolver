# MathLive LaTeX Compatibility

## Automatic Encapsulation

The `toLatex()` method automatically encapsulates subscripts and superscripts with braces for MathLive compatibility.

### Why This Matters

MathLive requires multi-character subscripts and superscripts to be properly braced to avoid parsing errors:

**❌ Without encapsulation (causes errors in MathLive):**
```latex
x_nm          → MathLive interprets as x_n followed by 'm'
E_0           → May cause issues
```

**✅ With encapsulation (works correctly):**
```latex
x_{nm}        → Correctly interpreted as 'x' with subscript 'nm'
E_{0}         → Correctly interpreted
```

### How It Works

The `_encapsulate_for_mathlive()` method:

1. **Finds unbraced multi-character scripts:**
   - `x_nm` → `x_{nm}`
   - `E_0` → `E_{0}`

2. **Preserves already-braced content:**
   - `x_{already}` → `x_{already}` (unchanged)

3. **Handles single characters intelligently:**
   - `x_n` → `x_n` (can stay unbraced)
   - `x^2` → `x^{2}` (braced for consistency)

4. **Merges adjacent scripts:**
   - `x_{n}m` → `x_{nm}` (merged)

### Examples

```python
from easyMathSolver.jupyter.formulas import FormulaParser

parser = FormulaParser()

# Multi-character subscripts are automatically encapsulated
parser.fromLatex("w_{nm}(E, E_0)")
print(parser.toLatex())
# Output: w_{nm}{\left(E,E_{0} \right)}

# Complex expressions work correctly
parser.fromLatex(r"e^{-\frac{E}{E_0}}")
print(parser.toLatex())
# Output: e^{- \frac{E}{E_{0}}}
```

### MathLive Editor Integration

When using the `.editor()` method, the widget receives properly encapsulated LaTeX:

```python
widget = parser.editor()
# MathLive receives: x_{nm} instead of x_nm
# No parsing errors!
```

### Technical Details

The encapsulation uses regex patterns to:
- Match `_` or `^` followed by alphanumeric characters
- Skip already braced content (`_{...}` or `^{...}`)
- Add braces around multi-character sequences
- Preserve single characters (though may brace them for consistency)

### Testing

To verify encapsulation is working:

```python
latex = parser.toLatex()

import re
# Should find no unbraced multi-char subscripts
unbraced = re.findall(r'_(?!\{)([a-zA-Z]{2,})', latex)
assert len(unbraced) == 0, "Found unbraced subscripts!"
```

## Benefits

✅ **No more MathLive parsing errors** from subscripts/superscripts
✅ **Automatic** - no manual LaTeX formatting needed
✅ **Consistent** - all expressions formatted the same way
✅ **SymPy compatible** - works with SymPy's latex() output
