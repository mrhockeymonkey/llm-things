# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal ASP.NET Core 9.0 Web API project named "proxyai". It uses the new minimal API approach with top-level statements in Program.cs.

## Development Commands

### Build and Run
```bash
dotnet build                    # Build the project
dotnet run                      # Run the application (uses launch settings)
dotnet watch run                # Run with hot reload during development
```

### Testing
Currently no test project is configured.

### Project Management
```bash
dotnet restore                  # Restore NuGet packages
dotnet clean                    # Clean build artifacts
```

## Architecture

### Project Structure
- **Program.cs**: Single entry point containing all application configuration, service registration, and endpoint mapping using minimal API style
- **appsettings.json / appsettings.Development.json**: Configuration files for logging and environment-specific settings
- **Properties/launchSettings.json**: Defines launch profiles with URLs (http://localhost:5185, https://localhost:7206)

### Technology Stack
- **.NET 9.0**: Target framework
- **ASP.NET Core Minimal APIs**: Uses top-level statements, no controllers
- **OpenAPI**: Configured for API documentation (enabled in Development environment at `/openapi/v1.json`)

### Current Endpoints
- `GET /weatherforecast`: Sample endpoint returning 5-day weather forecast

### Configuration
- HTTPS redirection enabled for all environments
- OpenAPI endpoint only mapped in Development environment
- Logging configured via appsettings.json (Information level default, Warning for ASP.NET Core)
