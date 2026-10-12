"""Run every test module in a fresh process.

Tkinter/macOS AppKit maintain process-global native state. Running multiple
Tk roots in one unittest interpreter can crash with Tcl_AsyncDelete even when
individual tests pass. Module isolation preserves all tests and exit codes.
"""
import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
def run():
    files=sorted(ROOT.glob('test_*.py'))
    failures=[]
    for file in files:
        print(f"=== {file.name} ===",flush=True)
        result=subprocess.run([sys.executable,'-m','unittest','-v',file.stem],cwd=ROOT)
        if result.returncode:
            failures.append((file.name,result.returncode))
    print(f"Test modules: {len(files)}; failed: {len(failures)}",flush=True)
    for name,code in failures:print(f"FAIL: {name} (exit {code})")
    return 1 if failures else 0
if __name__=='__main__':sys.exit(run())
