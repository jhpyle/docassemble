import sys
import time
import psutil

busy_pids = set()
index = 0

while True:
    busy_now = set()
    no_longer_busy = set()
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            if p.name() in ('apache2', 'uwsgi') and p.cpu_percent(interval=30.0) > 90.0:
                busy_now.add(pid)
        except:
            continue
    index += 1
    index = index % 6
    if index == 5:
        for pid in busy_pids:
            if not pid in busy_now:
                no_longer_busy.add(pid)
        for pid in no_longer_busy:
            busy_pids.discard(pid)
        for pid in busy_now:
            if pid in busy_pids:
                try:
                    p = psutil.Process(pid)
                    p.kill()
                except:
                    pass
                sys.stderr.write("Killed " + str(pid) + "\n")
                busy_pids.discard(pid)
            else:
                busy_pids.add(pid)
    time.sleep(5)
