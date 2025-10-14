# Custom LaTeX Parser

This directory contains the custom LaTeX parser for easyMathSolver (or whatever you rename the package to).

## Features

✅ **Automatic Building**: Parser automatically builds on first import
✅ **Auto-Install**: Automatically installs antlr4-tools if missing
✅ **Package-Agnostic**: Works regardless of package name
✅ **SymPy Integration**: Automatically patches SymPy to use custom grammar

## Files

- `LaTeX.g4` - Custom ANTLR4 grammar (modified from SymPy's version)
- `__init__.py` - Auto-builder and SymPy patcher
- `_build_custom_latex_parser.py` - Parser builder script
- `_antlr/` - Generated parser files (auto-created)

## How It Works

When you import the package:

```python
from easyMathSolver.main.manager import FormulaManager
```

The following happens automatically:

1. Package `__init__.py` imports `sympy` submodule
2. `sympy/__init__.py` checks if parser is built
3. If not built:
   - Checks if antlr4 is installed
   - If not, automatically installs it
   - Builds parser from LaTeX.g4
4. Patches SymPy's `parse_latex` to use custom parser
5. All LaTeX parsing in the project now uses custom grammar

## Manual Build

If you want to manually rebuild the parser:

```bash
cd /path/to/package/sympy
python _build_custom_latex_parser.py
```

Or use the build script:

```bash
cd /path/to/package/sympy
./build_parser.sh
```

## Customizing the Grammar

1. Edit `LaTeX.g4` with your custom ANTLR4 rules
2. Delete the `_antlr` directory: `rm -rf _antlr`
3. Restart Python - parser will auto-rebuild on next import

## Renaming the Package

The parser system is package-name agnostic. If you rename the package from `easyMathSolver` to something else, everything will continue to work without any code changes.

## Troubleshooting

**Parser not building automatically?**
```bash
pip install antlr4-tools
```

**Want to force rebuild?**
```bash
rm -rf _antlr
python _build_custom_latex_parser.py
```

**Check if custom parser is active:**
```python
import sympy.parsing.latex as latex_mod
print(latex_mod._antlr.__file__)
# Should show path to your custom _antlr, not SymPy's
```
