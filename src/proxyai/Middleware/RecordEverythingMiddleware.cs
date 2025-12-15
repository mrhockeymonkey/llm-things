using System.Text;
using System.Text.Json;

namespace proxyai.Middleware;

public class RequestResponseRecord
{
    public DateTime Timestamp { get; set; }
    public string Method { get; set; } = string.Empty;
    public string Path { get; set; } = string.Empty;
    public string QueryString { get; set; } = string.Empty;
    public string RequestBody { get; set; } = string.Empty;
    public string ResponseBody { get; set; } = string.Empty;
    public int StatusCode { get; set; }
}

public class RecordEverythingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly string _recordedDirectory;
    private static int _requestCounter = 0;

    public RecordEverythingMiddleware(RequestDelegate next)
    {
        _next = next;
        _recordedDirectory = Path.Combine(Directory.GetCurrentDirectory(), "recorded");

        // Create directory if it doesn't exist
        if (!Directory.Exists(_recordedDirectory))
        {
            Directory.CreateDirectory(_recordedDirectory);
        }
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Enable buffering to allow reading the body multiple times
        context.Request.EnableBuffering();

        // Read the request body
        string requestBody = string.Empty;
        if (context.Request.ContentLength > 0)
        {
            using var requestReader = new StreamReader(
                context.Request.Body,
                encoding: System.Text.Encoding.UTF8,
                detectEncodingFromByteOrderMarks: false,
                bufferSize: 1024,
                leaveOpen: true);

            requestBody = await requestReader.ReadToEndAsync();
            var json = JsonSerializer.Deserialize<JsonDocument>(requestBody);
            requestBody = JsonSerializer.Serialize(json, new JsonSerializerOptions()
            {
                WriteIndented = true
            });

            // Reset the stream position so downstream middleware can read it
            context.Request.Body.Position = 0;
        }

        // Capture the original response body stream
        var originalResponseBody = context.Response.Body;

        // Replace with a MemoryStream to capture the response
        using var responseBodyStream = new MemoryStream();
        context.Response.Body = responseBodyStream;

        await _next(context);

        // Read the response body from the MemoryStream
        responseBodyStream.Seek(0, SeekOrigin.Begin);
        string responseBody = await new StreamReader(
            responseBodyStream, 
            encoding: System.Text.Encoding.UTF8,
            detectEncodingFromByteOrderMarks: false, 
            leaveOpen: true).ReadToEndAsync();

        // Copy the captured response back to the original stream
        responseBodyStream.Seek(0, SeekOrigin.Begin);
        await responseBodyStream.CopyToAsync(originalResponseBody);

        // Restore the original response body stream
        context.Response.Body = originalResponseBody;

        // Create record object
        var record = new RequestResponseRecord
        {
            Timestamp = DateTime.UtcNow,
            Method = context.Request.Method,
            Path = context.Request.Path.ToString(),
            QueryString = context.Request.QueryString.ToString(),
            RequestBody = requestBody,
            ResponseBody = responseBody,
            StatusCode = context.Response.StatusCode
        };

        // Write to individual JSON file
        await WriteRecordToFileAsync(record);
    }

    private async Task WriteRecordToFileAsync(RequestResponseRecord record)
    {
        // Generate unique filename with timestamp and sequential counter
        var timestamp = record.Timestamp.ToString("yyyyMMdd_HHmmss");
        var counter = Interlocked.Increment(ref _requestCounter);
        var filename = $"{timestamp}_{counter:D3}.json";
        var filePath = Path.Combine(_recordedDirectory, filename);

        // Serialize to JSON with indentation
        var json = JsonSerializer.Serialize(record, new JsonSerializerOptions
        {
            WriteIndented = true
        });

        // Write to file
        await File.WriteAllTextAsync(filePath, json);
    }
}