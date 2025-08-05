using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Service for handling file operations related to parser validation
    /// </summary>
    public interface IFileService
    {
        /// <summary>
        /// Reads exclusion list from CSV file
        /// </summary>
        /// <param name="filePath">Path to the CSV file</param>
        /// <returns>List of excluded parser names</returns>
        Task<List<string>> ReadExclusionListAsync(string filePath);

        /// <summary>
        /// Filters YAML files from a list of file paths
        /// </summary>
        /// <param name="filePaths">List of file paths</param>
        /// <returns>List of YAML file paths</returns>
        List<string> FilterYamlFiles(IEnumerable<string> filePaths);

        /// <summary>
        /// Checks if a file exists
        /// </summary>
        /// <param name="filePath">Path to the file</param>
        /// <returns>True if file exists, false otherwise</returns>
        bool FileExists(string filePath);

        /// <summary>
        /// Reads all text from a file
        /// </summary>
        /// <param name="filePath">Path to the file</param>
        /// <returns>File content as string</returns>
        Task<string> ReadAllTextAsync(string filePath);
    }

    /// <summary>
    /// Implementation of file service for parser validation
    /// </summary>
    public class FileService : IFileService
    {
        private readonly ILogger<FileService> _logger;

        public FileService(ILogger<FileService> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <inheritdoc />
        public async Task<List<string>> ReadExclusionListAsync(string filePath)
        {
            try
            {
                if (!File.Exists(filePath))
                {
                    _logger.LogWarning("Exclusion list file not found at path: {FilePath}", filePath);
                    return new List<string>();
                }

                var lines = await File.ReadAllLinesAsync(filePath);
                var exclusionList = new List<string>();

                foreach (var line in lines)
                {
                    if (!string.IsNullOrWhiteSpace(line))
                    {
                        // Handle CSV format - take the first column
                        var parts = line.Split(',');
                        if (parts.Length > 0 && !string.IsNullOrWhiteSpace(parts[0]))
                        {
                            exclusionList.Add(parts[0].Trim());
                        }
                    }
                }

                _logger.LogInformation("Read {Count} entries from exclusion list", exclusionList.Count);
                return exclusionList;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading exclusion list from file: {FilePath}", filePath);
                return new List<string>();
            }
        }

        /// <inheritdoc />
        public List<string> FilterYamlFiles(IEnumerable<string> filePaths)
        {
            if (filePaths == null)
            {
                return new List<string>();
            }

            var yamlFiles = filePaths
                .Where(path => !string.IsNullOrWhiteSpace(path) && path.EndsWith(".yaml", StringComparison.OrdinalIgnoreCase))
                .ToList();

            _logger.LogInformation("Filtered {Count} YAML files from {TotalCount} total files", yamlFiles.Count, filePaths.Count());
            return yamlFiles;
        }

        /// <inheritdoc />
        public bool FileExists(string filePath)
        {
            try
            {
                return File.Exists(filePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking if file exists: {FilePath}", filePath);
                return false;
            }
        }

        /// <inheritdoc />
        public async Task<string> ReadAllTextAsync(string filePath)
        {
            try
            {
                if (!File.Exists(filePath))
                {
                    throw new FileNotFoundException($"File not found: {filePath}");
                }

                return await File.ReadAllTextAsync(filePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading file: {FilePath}", filePath);
                throw;
            }
        }
    }
}
