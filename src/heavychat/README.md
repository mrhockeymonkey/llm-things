
```bash
htop -p $(pgrep -f heavychat.py)

# how many open file descriptors can you have 
ulimit -n
1024

# watch open files for process
watch -n 1 "ls -l /proc/$(pgrep -f heavychat.py)/fd | wc -l"
14
```

1000 = 63s