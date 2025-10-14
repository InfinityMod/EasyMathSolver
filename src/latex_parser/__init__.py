"""
Custom LaTeX parser for easyMathSolver
Automatically builds and patches SymPy to use custom LaTeX.g4 grammar
"""
import os
import sys

# Get the package root directory (parent of this latex_parser folder)
_package_root = os.path.dirname(os.path.dirname(__file__))
_package_name = os.path.basename(_package_root)

# Add package root to path to ensure imports work
if _package_root not in sys.path:
    sys.path.insert(0, _package_root)


def get_parser_module():
    """Get the parser builder module dynamically based on actual package name"""
    try:
        # Import using the actual package name
        import importlib
        return importlib.import_module(f'{_package_name}.latex_parser._build_custom_latex_parser')
    except ImportError:
        # Fallback: import from current directory
        from . import _build_custom_latex_parser
        return _build_custom_latex_parser


def ensure_parser_built():
    """
    Automatically build the custom parser if not already built.
    This runs on import to ensure the parser is always ready.
    """
    antlr_dir = os.path.join(os.path.dirname(__file__), "_antlr")
    parser_exists = os.path.exists(os.path.join(antlr_dir, "latexlexer.py"))

    if not parser_exists:
        print(f"🔧 Building custom LaTeX parser for {_package_name}...")
        try:
            builder = get_parser_module()
            success = builder.build_custom_parser(force=False)
            if success:
                print("✅ Custom parser built successfully!")
            else:
                print("⚠️  Parser build skipped (antlr4 not available)")
                print("   Installing antlr4-tools...")
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "antlr4-tools", "-q"])
                    print("✅ antlr4-tools installed! Building parser...")
                    success = builder.build_custom_parser(force=True)
                    if success:
                        print("✅ Custom parser built successfully!")
                except Exception as e:
                    print(f"⚠️  Could not auto-install antlr4-tools: {e}")
                    print(f"   Manual install: pip install antlr4-tools")
        except Exception as e:
            print(f"⚠️  Could not build custom parser: {e}")
            print("   Will use SymPy's default parser")

    return parser_exists or os.path.exists(os.path.join(antlr_dir, "latexlexer.py"))


def patch_sympy():
    """Patch SymPy to use our custom LaTeX parser"""
    if not ensure_parser_built():
        return False

    try:
        import sympy.parsing.latex as sympy_latex

        # Import our custom parser module
        import importlib
        custom_antlr = importlib.import_module(f'{_package_name}.latex_parser._antlr')

        # Patch SymPy to use it
        sympy_latex._antlr = custom_antlr
        print(f"✓ {_package_name}: Using custom LaTeX parser")
        return True
    except Exception as e:
        print(f"⚠️  Could not patch SymPy: {e}")
        print("   Using SymPy's default parser")
        return False


# Automatically patch on import
patch_sympy()
