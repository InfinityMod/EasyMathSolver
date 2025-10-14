"""
easyMathSolver - Easy Mathematical Expression Solver
Uses a custom LaTeX grammar for improved parsing
"""
import os
import sys

# Get package name dynamically to support renaming
__package_name__ = __name__.split('.')[0]

# Automatically build and patch SymPy to use custom LaTeX parser
# This is done by importing the latex_parser submodule which handles everything
try:
    from . import latex_parser as _custom_latex
except ImportError as e:
    print(f"⚠️  Could not load custom LaTeX parser: {e}")
    print("   Using SymPy's default LaTeX parser")

__version__ = "1.0.0"
__all__ = ["FormulaManager", "FormulaParser"]
