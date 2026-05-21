"""Entry point for Railpack auto-detect (expects main.py at project root)."""
import runpy

if __name__ == "__main__":
    runpy.run_module("src.main", run_name="__main__")
