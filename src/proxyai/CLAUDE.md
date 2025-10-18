# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a reverse proxy server built with ASP.NET Core 9.0 and YARP (Yet Another Reverse Proxy) to intercept and inspect API calls. Its primary purpose is to allow debugging and inspection of requests/responses sent to LLM APIs (OpenAI, Anthropic, etc.) by acting as a transparent proxy.

## Development Commands

### Build and Run
```bash
dotnet build                    # Build the project
dotnet run                      # Run the application (uses launch settings)
dotnet watch run                # Run with hot reload during development
```

### Using the Proxy
```bash
# Set Claude Code to use the proxy for debugging
export ANTHROPIC_BASE_URL=http://localhost:5185
claude
```

### Project Management
```bash
dotnet restore                  # Restore NuGet packages
dotnet clean                    # Clean build artifacts
```

## Architecture

### Core Components
- **YARP Reverse Proxy**: Microsoft's lightweight reverse proxy library configured in-memory
- **Request Inspection Middleware**: Custom middleware at Program.cs:24-57 that logs all requests (method, path, headers, body) before forwarding to backend
- **In-Memory Route Configuration**: Routes and clusters defined in GetRoutes() and GetClusters() methods

### Proxy Configuration

All routing is configured in Program.cs via two static methods:

**Routes** (Program.cs:70-95):
- `openai` route: Matches requests with Host header "api.openai.com", catches all paths
- `sim` route: Matches paths starting with "/simulate/", routes to Anthropic API

**Clusters** (Program.cs:98-136):
- `openai` cluster: Forwards to https://api.openai.com
- `sim` cluster: Forwards to https://api.anthropic.com

### Request Flow
1. Client sends request to localhost:5185 (HTTP) or localhost:7206 (HTTPS)
2. Inspection middleware captures and logs: method, path, query string, headers, body
3. Request body buffering enabled to allow multiple reads
4. YARP routes request based on Host header or path pattern
5. Request forwarded to configured backend (OpenAI or Anthropic)
6. Response returned to client

### Key Dependencies
- **Yarp.ReverseProxy 2.3.0**: Core proxy functionality
- **Microsoft.AspNetCore.OpenApi 9.0.0**: API documentation support

### Debugging
- Set breakpoint at Program.cs:27 to inspect incoming requests
- Console logging outputs request details without breakpoint
- Request body buffering allows inspection without breaking the stream
