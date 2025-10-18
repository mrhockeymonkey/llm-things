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
        
        await _next(context);
        
        
        
        // Read the request body
        string responseBody = string.Empty;
        using var responseReader = new StreamReader(
            context.Response.Body,
            encoding: System.Text.Encoding.UTF8,
            detectEncodingFromByteOrderMarks: false,
            bufferSize: 1024,
            leaveOpen: true);

        responseBody = await responseReader.ReadToEndAsync();

        // Reset the stream position so downstream middleware can read it
        context.Response.Body.Position = 0;
        
        
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