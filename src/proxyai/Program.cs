using proxyai.Transforms;
using Yarp.ReverseProxy.Configuration;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options =>
{
    // options.Limits.MaxConcurrentConnections = 10000;
    // options.Limits.MaxConcurrentUpgradedConnections = 10000;
    // options.Limits.Http2.MaxStreamsPerConnection = 1000;
});

builder.Services.AddOpenApi();

// Add YARP reverse proxy services
builder.Services.AddReverseProxy()
    .LoadFromMemory(GetRoutes(), GetClusters())
    .AddTransforms(context =>
    {
        if (context.Route.RouteId == "openai-v1")
        {
            // OPTION fake the output of /v1/chat/completion
            context.RequestTransforms.Add(new FakeChatCompletionRequestTransform());
        }
    });

var app = builder.Build();

app.MapOpenApi();
app.UseHttpsRedirection();

// OPTION Uncomment to log request/response to log.txt
//app.UseMiddleware<RecordEverythingMiddleware>();

app.MapReverseProxy();

app.Run();

// Configure YARP routes
static RouteConfig[] GetRoutes()
{
    return
    [
        new RouteConfig
        {
            RouteId = "openai-v1",
            ClusterId = "openai",
            Match = new RouteMatch
            {
                Path = "/openai/v1/{**catch-all}"
            },
            Transforms = new[]
            {
                new Dictionary<string, string>
                {
                    ["PathPattern"] = "/v1/{**catch-all}"
                }
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
            ClusterId = "openai",
            Destinations = new Dictionary<string, DestinationConfig>
            {
                ["destination1"] = new DestinationConfig
                {
                    Address = "https://api.openai.com"
                }
            }
        }
        // new ClusterConfig
        // {
        //     ClusterId = "sim",
        //     Destinations = new Dictionary<string, DestinationConfig>
        //     {
        //         ["destination1"] = new DestinationConfig
        //         {
        //             Address = "https://api.anthropic.com"
        //         }
        //     }
        // },
        // new ClusterConfig
        // {
        //     ClusterId = "sim",
        //     Destinations = new Dictionary<string, DestinationConfig>
        //     {
        //         ["destination1"] = new DestinationConfig
        //         {
        //             Address = "https://api.anthropic.com"
        //         }
        //     }
        // }
    ];
}

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
