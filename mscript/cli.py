# mscript/cli.py

import runpy
import os

def main():
    it_path = os.path.join(os.path.dirname(__file__), "it.py")
    runpy.run_path(it_path, run_name="__main__")

if __name__ == "__main__":
    main()