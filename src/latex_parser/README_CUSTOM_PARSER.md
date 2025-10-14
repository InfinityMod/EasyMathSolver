# Custom LaTeX Parser for easyMathSolver

This project uses a custom `LaTeX.g4` grammar file (modified from SymPy's version) for parsing LaTeX expressions.

## Setup

### Option 1: Install antlr4 and build from grammar (Recommended)

```bash
# Install antlr4-tools
pip install antlr4-tools

# Build the custom parser
cd /path/to/easyMathSolver
python _build_custom_latex_parser.py
```

### Option 2: Use pre-built parser files

If you don't want to install antlr4, you can use the pre-generated parser files in `_antlr/` directory.

## How It Works

1. The custom `LaTeX.g4` grammar file is in the root of easyMathSolver package
2. When imported, easyMathSolver patches SymPy's `parse_latex` to use the custom parser
3. All LaTeX parsing throughout the project uses the custom grammar

## Updating the Grammar

1. Edit `LaTeX.g4` with your custom rules
2. Rebuild the parser:
   ```bash
   python _build_custom_latex_parser.py
   ```
3. The generated files in `_antlr/` will be updated

## Files

- `LaTeX.g4` - Custom ANTLR grammar for LaTeX
- `_build_custom_latex_parser.py` - Script to build parser from grammar
- `_antlr/` - Generated parser files (lexer, parser, etc.)
- `__init__.py` - Patches SymPy to use custom parser
