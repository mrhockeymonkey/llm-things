
```bash
htop -p $(pgrep -f heavychat.py)

# how many open file descriptors can you have 
ulimit -n
1024

# watch open files for process
watch -n 1 "ls -l /proc/$(pgrep -f heavychat.py)/fd | wc -l"
14
```

heavychat.py

httpx=5000 sem=1000 count=5000 time=184s
httpx=5000 sem=2000 count=5000 time=181s
httpx=5000 sem=5000 count=5000 time=159s

heavychat_aiometer.py

httpx=5000 sem=1000 count=5000 time=163
httpx=5000 sem=2000 count=5000 time=160
httpx=5000 sem=5000 count=5000 time=161