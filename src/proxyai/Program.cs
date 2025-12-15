using Microsoft.AspNetCore.HttpLogging;
using NReco.Logging.File;
using proxyai.Middleware;
using proxyai.Transforms;
using Yarp.ReverseProxy.Configuration;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options =>
{
    // options.Limits.MaxConcurrentConnections = 10_000;
    // options.Limits.MaxConcurrentUpgradedConnections = 10_000;
    // options.Limits.Http2.MaxStreamsPerConnection = 1000;
});

builder.Services.AddOpenApi();
builder.Services.AddLogging(options =>
{
    options.AddFile("log.txt", append: false);
});
builder.Services.AddHttpLogging(options =>
{
    options.LoggingFields = HttpLoggingFields.RequestMethod | 
                            HttpLoggingFields.RequestPath |
                            HttpLoggingFields.ResponseStatusCode |
                            HttpLoggingFields.RequestBody |
                            HttpLoggingFields.ResponseBody
        ;
    options.CombineLogs = true;
    options.MediaTypeOptions.AddText("application/json");
    options.RequestBodyLogLimit = Int32.MaxValue;
    options.ResponseBodyLogLimit = Int32.MaxValue;
});

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

app.UseHttpLogging();
app.MapOpenApi();

// OPTION Uncomment to log request/response to log.txt
File.Delete("recorded.txt");
app.UseMiddleware<RecordEverythingMiddleware>();

app.MapGet("/", () => Results.Json(new {hello = "world"}));
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
        },
        new RouteConfig
        {
            RouteId = "claude",
            ClusterId = "claude",
            Match = new RouteMatch
            {
                Path = "/claude/{**catch-all}"
            },
            Transforms = new[]
            {
                new Dictionary<string, string>
                {
                    ["PathPattern"] = "/{**catch-all}"
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
        },
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
        new ClusterConfig
        {
            ClusterId = "claude",
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
