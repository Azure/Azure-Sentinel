using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Configuration;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Service for Git operations related to parser validation
    /// </summary>
    public interface IGitService
    {
        /// <summary>
        /// Gets the list of modified files compared to upstream master
        /// </summary>
        /// <param name="currentDirectory">Current working directory</param>
        /// <param name="targetPath">Path to check for modifications</param>
        /// <returns>List of modified file paths</returns>
        Task<List<string>> GetModifiedFilesAsync(string currentDirectory, string targetPath);

        /// <summary>
        /// Gets the current commit hash
        /// </summary>
        /// <returns>Current commit hash</returns>
        Task<string?> GetCurrentCommitHashAsync();

        /// <summary>
        /// Ensures upstream remote is configured and fetched
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        Task<bool> EnsureUpstreamRemoteAsync();
    }

    /// <summary>
    /// Implementation of Git service for parser validation
    /// </summary>
    public class GitService : IGitService
    {
        private readonly ILogger<GitService> _logger;

        public GitService(ILogger<GitService> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <inheritdoc />
        public async Task<List<string>> GetModifiedFilesAsync(string currentDirectory, string targetPath)
        {
            try
            {
                // Ensure upstream remote is configured
                await EnsureUpstreamRemoteAsync();

                var command = $"git diff --name-only upstream/master {targetPath}";
                var result = await ExecuteGitCommandAsync(command, currentDirectory);

                if (result.Success && !string.IsNullOrWhiteSpace(result.Output))
                {
                    var modifiedFiles = result.Output
                        .Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
                        .Where(line => !string.IsNullOrWhiteSpace(line))
                        .ToList();

                    _logger.LogInformation("Found {Count} modified files", modifiedFiles.Count);
                    return modifiedFiles;
                }

                _logger.LogWarning("No modified files found or git command failed");
                return new List<string>();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting modified files from git");
                return new List<string>();
            }
        }

        /// <inheritdoc />
        public async Task<string?> GetCurrentCommitHashAsync()
        {
            try
            {
                var command = "git rev-parse HEAD";
                var result = await ExecuteGitCommandAsync(command);

                if (result.Success && !string.IsNullOrWhiteSpace(result.Output))
                {
                    var commitHash = result.Output.Trim();
                    _logger.LogInformation("Current commit hash: {CommitHash}", commitHash);
                    return commitHash;
                }

                _logger.LogWarning("Failed to get current commit hash");
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting current commit hash");
                return null;
            }
        }

        /// <inheritdoc />
        public async Task<bool> EnsureUpstreamRemoteAsync()
        {
            try
            {
                // Check if upstream remote exists
                var checkRemoteResult = await ExecuteGitCommandAsync("git remote");
                
                if (checkRemoteResult.Success && !checkRemoteResult.Output.Contains("upstream"))
                {
                    // Add upstream remote
                    var addUpstreamCommand = $"git remote add upstream '{ValidationConstants.SentinelRepoUrl}'";
                    var addResult = await ExecuteGitCommandAsync(addUpstreamCommand);
                    
                    if (!addResult.Success)
                    {
                        _logger.LogError("Failed to add upstream remote");
                        return false;
                    }
                    
                    _logger.LogInformation("Added upstream remote");
                }

                // Fetch from upstream
                var fetchResult = await ExecuteGitCommandAsync("git fetch upstream");
                
                if (!fetchResult.Success)
                {
                    _logger.LogError("Failed to fetch from upstream");
                    return false;
                }

                _logger.LogInformation("Successfully fetched from upstream");
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error ensuring upstream remote");
                return false;
            }
        }

        /// <summary>
        /// Executes a git command and returns the result
        /// </summary>
        /// <param name="command">The git command to execute</param>
        /// <param name="workingDirectory">Working directory for the command</param>
        /// <returns>Command execution result</returns>
        private async Task<CommandResult> ExecuteGitCommandAsync(string command, string? workingDirectory = null)
        {
            try
            {
                using var process = new Process();
                
                process.StartInfo.FileName = "git";
                process.StartInfo.Arguments = command.Replace("git ", "");
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                
                if (!string.IsNullOrWhiteSpace(workingDirectory))
                {
                    process.StartInfo.WorkingDirectory = workingDirectory;
                }

                _logger.LogDebug("Executing git command: {Command}", command);

                process.Start();
                
                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();
                
                await process.WaitForExitAsync();

                var success = process.ExitCode == 0;
                
                if (!success)
                {
                    _logger.LogError("Git command failed with exit code {ExitCode}. Error: {Error}", 
                        process.ExitCode, error);
                }

                return new CommandResult
                {
                    Success = success,
                    Output = output,
                    Error = error,
                    ExitCode = process.ExitCode
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Exception executing git command: {Command}", command);
                return new CommandResult
                {
                    Success = false,
                    Error = ex.Message,
                    ExitCode = -1
                };
            }
        }

        /// <summary>
        /// Represents the result of a command execution
        /// </summary>
        private class CommandResult
        {
            public bool Success { get; set; }
            public string Output { get; set; } = string.Empty;
            public string Error { get; set; } = string.Empty;
            public int ExitCode { get; set; }
        }
    }
}
