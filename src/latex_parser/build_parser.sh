#!/bin/bash
# Build custom LaTeX parser for easyMathSolver

echo "=== Building Custom LaTeX Parser ==="
echo ""

# Check if antlr4 is installed
if ! command -v antlr4 &> /dev/null; then
    echo "❌ antlr4 not found!"
    echo ""
    echo "Installing antlr4-tools..."
    pip install antlr4-tools

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install antlr4-tools"
        exit 1
    fi
fi

echo "✓ antlr4 found"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Run the build script
echo "Building parser from LaTeX.g4..."
python _build_custom_latex_parser.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Custom LaTeX parser built successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Restart your Python/Jupyter session"
    echo "  2. Import easyMathSolver - it will use the custom parser automatically"
else
    echo ""
    echo "❌ Failed to build parser"
    exit 1
fi
