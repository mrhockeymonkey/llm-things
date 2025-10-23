using Yarp.ReverseProxy.Transforms;

namespace proxyai.Transforms;

/// <summary>
/// This request transform mocks the output of /v1/chat/completion
/// YARP will see that s status code is set which will result in no more transforms and no proxying
/// </summary>
public class FakeChatCompletionRequestTransform : RequestTransform
{
    public override async ValueTask ApplyAsync(RequestTransformContext context)
    {
        if (context.Path != "/v1/chat/completions") return;

        await Task.Delay(TimeSpan.FromSeconds(10));
        
        // Set response headers
        context.HttpContext.Response.StatusCode = 200;
        context.HttpContext.Response.ContentType = "application/json";
        
        // Write fake OpenAI-compatible response
        var fakeResponse = FakeResponse();
        
        await context.HttpContext.Response.WriteAsJsonAsync(fakeResponse);
        Console.WriteLine("[Fake Response] Returned fake OpenAI response");
    }

    private static object FakeResponse()
    {
        var fakeResponse = new
        {
            id = "fake-response-" + Guid.NewGuid().ToString(),
            @object = "chat.completion",
            created = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            model = "gpt-4",
            choices = new[]
            {
                new
                {
                    index = 0,
                    message = new
                    {
                        role = "assistant",
                        content = "This is a fake response from the proxy!"
                    },
                    finish_reason = "stop"
                }
            },
            usage = new
            {
                prompt_tokens = 10,
                completion_tokens = 10,
                total_tokens = 20
            }
        };
        return fakeResponse;
    }
}
