"""Mac packaged-app resource smoke test; not a thermal measurement."""
import subprocess,sys,time
from pathlib import Path
import psutil
exe=Path('dist/ACE Adventures 3.app/Contents/MacOS/ACE Adventures 3')
if sys.platform!='darwin':raise SystemExit('macOS required')
assert exe.is_file(),exe
proc=subprocess.Popen([str(exe.resolve())],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    root=psutil.Process(proc.pid)
    samples=[]
    time.sleep(2)
    for _ in range(12):
        if proc.poll() is not None:
            out,err=proc.communicate(timeout=3)
            raise AssertionError('Packaged app exited: '+err.decode(errors='replace')[-3000:])
        children=root.children(recursive=True)
        group=[root]+[p for p in children if p.is_running()]
        rss=0;cpu=0
        for p in group:
            try:
                rss+=p.memory_info().rss
                cpu+=p.cpu_percent(interval=None)
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
        samples.append((rss,cpu))
        time.sleep(1)
    peak=max(r for r,c in samples)/1048576
    avg_cpu=sum(c for r,c in samples[3:])/max(1,len(samples)-3)
    print(f'Idle packaged app: peak RSS={peak:.1f} MiB, average CPU={avg_cpu:.1f}%')
    assert peak<700, f'Idle memory exceeds smoke budget: {peak:.1f} MiB'
    assert avg_cpu<75, f'Idle CPU exceeds smoke budget: {avg_cpu:.1f}%'
finally:
    proc.terminate()
    try:proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill();proc.communicate()
