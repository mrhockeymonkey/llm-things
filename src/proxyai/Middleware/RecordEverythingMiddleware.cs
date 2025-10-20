using System.Text;

namespace proxyai.Middleware;

public class RecordEverythingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly string _logFilePath;
    private readonly SemaphoreSlim _fileLock = new(1, 1);

    public RecordEverythingMiddleware(RequestDelegate next)
    {
        _next = next;
        _logFilePath = Path.Combine(Directory.GetCurrentDirectory(), "log.txt");
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

        var logEntry = new StringBuilder();
        logEntry.AppendLine($"=== {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss.fff} UTC ===");
        logEntry.AppendLine($"Method: {context.Request.Method}");
        logEntry.AppendLine($"Path: {context.Request.Path}{context.Request.QueryString}");
        logEntry.AppendLine("Headers:");
        foreach (var header in context.Request.Headers)
        {
            logEntry.AppendLine($"  {header.Key}: {header.Value}");
        }
        logEntry.AppendLine("Request Body:");
        logEntry.AppendLine(requestBody);
        logEntry.AppendLine("Response Body:");
        logEntry.AppendLine(responseBody);
        logEntry.AppendLine("---");


        // Write to log file
        await WriteToLogFileAsync(logEntry);
    }

    private async Task WriteToLogFileAsync(StringBuilder logEntry)
    {
        await _fileLock.WaitAsync();
        try
        {
            await File.AppendAllTextAsync(_logFilePath, logEntry.ToString());
        }
        finally
        {
            _fileLock.Release();
        }
    }
}