"""Run each test module in a fresh interpreter.

Tkinter creates thread-affine Tcl interpreters; macOS can abort when test modules
construct/destroy separate roots while Tcl objects remain awaiting GC in a later
module. Fresh processes isolate these lifetimes and preserve all test coverage.
"""
import pathlib
import subprocess
import sys

def main():
    modules=sorted(p.stem for p in pathlib.Path(__file__).parent.glob("test_*.py"))
    failed=[]
    for name in modules:
        print(f"\n=== {name} ===",flush=True)
        result=subprocess.run([sys.executable,"-m","unittest","-v",name],check=False)
        if result.returncode:
            failed.append((name,result.returncode))
    if failed:
        print("FAILED TEST MODULES:",failed,flush=True)
        return 1
    print(f"PASS: {len(modules)} isolated test modules",flush=True)
    return 0

if __name__=="__main__":
    sys.exit(main())
