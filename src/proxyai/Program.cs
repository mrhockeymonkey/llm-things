using Yarp.ReverseProxy.Configuration;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

// Add YARP reverse proxy services
builder.Services.AddReverseProxy()
    .LoadFromMemory(GetRoutes(), GetClusters());

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

// Middleware to inspect requests before YARP processes them
app.Use(async (context, next) =>
{
    // Set breakpoint here to inspect the request
    var method = context.Request.Method;
    var path = context.Request.Path;
    var queryString = context.Request.QueryString;
    var headers = context.Request.Headers;

    // Enable buffering to allow reading the body multiple times
    context.Request.EnableBuffering();

    // Read the request body
    string requestBody = string.Empty;
    if (context.Request.ContentLength > 0)
    {
        using var reader = new StreamReader(
            context.Request.Body,
            encoding: System.Text.Encoding.UTF8,
            detectEncodingFromByteOrderMarks: false,
            bufferSize: 1024,
            leaveOpen: true);

        requestBody = await reader.ReadToEndAsync();

        // Reset the stream position so downstream middleware can read it
        context.Request.Body.Position = 0;
    }

    // Log request details (useful for debugging without breakpoint)
    Console.WriteLine($"[Request] {method} {path}{queryString}");
    Console.WriteLine($"[Body] {requestBody}");

    await next();
});

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

// Map the reverse proxy
app.MapReverseProxy();

app.Run();

// Configure YARP routes
static RouteConfig[] GetRoutes()
{
    return
    [
        new RouteConfig
        {
            RouteId = "route1",
            ClusterId = "cluster1",
            Match = new RouteMatch
            {
                Path = "{**catch-all}"
            }
        }
    ];
}

// Configure YARP clusters (backend services)
static ClusterConfig[] GetClusters()
{
    return
    [
        new ClusterConfig
        {
            ClusterId = "cluster1",
            Destinations = new Dictionary<string, DestinationConfig>
            {
                ["destination1"] = new DestinationConfig
                {
                    Address = "https://api.anthropic.com"
                }
            }
        }
    ];
}

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
