# proxyai

To see what claude code is actually doing

```bash
# to inspect claude requests
export ANTHROPIC_BASE_URL=http://localhost:5185/claude
claude

# check connections (legacy event counter)
dotnet counters monitor -n proxyai --counters Microsoft-AspNetCore-Server-Kestrel
```