using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.IO;

Console.WriteLine("===============================================");
Console.WriteLine("      Intel VDA: Real-Time Log Mode            ");
Console.WriteLine("===============================================");

// 1. Path Resolution
string baseDir = AppContext.BaseDirectory;
// Adjusted pathing to find the root from the publish folder
string rootDir = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", "..", ".."));
string serverScript = Path.Combine(rootDir, "backend", "server.py");

// 2. Prepare Command - Added --no-capture-output
string dbPath = args.Length > 0 ? args[0] : "vda_intelligence.db";
// IMPORTANT: --no-capture-output tells conda NOT to buffer the python logs
string command = $"run --no-capture-output -n intel-vda-env python \"{serverScript}\" --db_path \"{dbPath}\"";

Console.WriteLine($"[EXEC] Starting: conda {command}");

ProcessStartInfo psi = new ProcessStartInfo
{
    FileName = "conda",
    Arguments = command,
    UseShellExecute = false, 
    CreateNoWindow = false, // Allow it to print to THIS terminal
    WorkingDirectory = rootDir
};

try {
    using Process proc = Process.Start(psi);
    Console.WriteLine("[SYSTEM] Backend connected to this terminal. Waiting for logs...");
    proc.WaitForExit(); 
}
catch (Exception ex) {
    Console.WriteLine($"[CRITICAL] Launcher error: {ex.Message}");
}