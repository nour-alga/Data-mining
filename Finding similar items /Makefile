# =====================================================
# Makefile for the "Finding Similar Items" Project
# =====================================================
# Author: Alga Nour - Karim 
# Description:
# This Makefile automates running and cleaning the Python
# project for document similarity using LSH (Locality Sensitive Hashing).

# Python command
PYTHON = python3

# Main script (entry point)
MAIN = Test.py

# =====================================================
# Run the main program
# =====================================================
run:
	@echo ">>> Running the Finding Similar Items project..."
	$(PYTHON) $(MAIN)
	@echo ">>> Execution complete!"

# =====================================================
# Clean generated cache files
# =====================================================
clean:
	@echo ">>> Cleaning up temporary files..."
	rm -rf __pycache__ */__pycache__ *.pyc
	@echo ">>> Cleanup complete!"

# =====================================================
# Show available commands
# =====================================================
help:
	@echo "Available commands:"
	@echo "  make run      - Run the main Python script (Test.py)"
	@echo "  make clean    - Remove cache files"
	@echo "  make help     - Display this help message"
