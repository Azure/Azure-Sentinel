using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Azure.Storage.Blobs;

namespace Varonis.Sentinel.Functions.State;

public class BlobStateSaver
{
    private readonly string _connectionString;
    private BlobClient _blobClient;
    private bool _isInitialized;

    public BlobStateSaver(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task Init()
    {
        const string containerName = "varonis-files";
        const string blobName = "varonis-state.txt";
        var containerClient = new BlobContainerClient(_connectionString, containerName);
        await containerClient.CreateIfNotExistsAsync();

        _blobClient = containerClient.GetBlobClient(blobName);

        _isInitialized = true;
    }

    public async Task<DateTime?> GetLastDate()
    {
        CheckIfInitialized();

        if (!await _blobClient.ExistsAsync()) return null;
        var result = await _blobClient.DownloadContentAsync();
        var utcString = result.Value.Content.ToString();
        return DateTime.Parse(utcString, null, System.Globalization.DateTimeStyles.RoundtripKind);
    }

    public async Task SaveLastDate(DateTime dateToSave)
    {
        CheckIfInitialized();

        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(dateToSave.ToString("u")));
        await _blobClient.UploadAsync(stream, true);
    }

    private void CheckIfInitialized()
    {
        if (!_isInitialized)
            throw new Exception($"{nameof(BlobStateSaver)} is not initialized");
    }
}