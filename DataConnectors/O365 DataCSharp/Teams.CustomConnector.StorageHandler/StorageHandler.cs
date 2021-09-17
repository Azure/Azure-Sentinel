using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Specialized;
using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Teams.CustomConnector.Common;
using Constants = Teams.CustomConnector.Common.Constants;

/// <summary>
/// 
/// </summary>
namespace Teams.CustomConnector.StorageHandler
{

    /// <summary></summary>
    public enum OperationType
    {
        Data,
        Log
    }

    /// <summary></summary>
    public class StorageHandler
    {
        readonly ILogger log;
        private BlobServiceClient blobServiceClient;
        public StorageHandler(ILogger log)
        {
            this.log = log;
        
        }


        /// <summary>Uploads the data to container asynchronous.</summary>
        /// <param name="opType">Type of the op.</param>
        /// <param name="blobName">Name of the BLOB.</param>
        /// <param name="data">The data.</param>
        public async Task UploadDataToContainerAsync(OperationType opType, string blobName, OperationDetails operationDetails)
        {
            log.LogInformation(Common.Constants.UploadDataToStorageContainerStarted);
            try
            {
                CreateCloudStroageHandler();
                var container = blobServiceClient.GetBlobContainerClient(opType == OperationType.Data ? Environment.GetEnvironmentVariable(Constants.DataContainerName) : Environment.GetEnvironmentVariable(Constants.LogContainerName));
                var blockBlob = container.GetBlockBlobClient(blobName);
                var data = JsonSerializer.Serialize(operationDetails);
                byte[] byteArray = Encoding.ASCII.GetBytes(data);
                MemoryStream stream = new MemoryStream(byteArray);
                await blockBlob.UploadAsync(stream);
                log.LogInformation(Common.Constants.UploadDataToStorageContainerCompleted);
            }
            catch (Exception ex)
            {
                log.LogError(ex.InnerException.ToString());
                throw;
            }
        }

        /// <summary>Uploads the data to container asynchronous.</summary>
        /// <param name="opType">Type of the op.</param>
        /// <param name="blobName">Name of the BLOB.</param>
        /// <param name="data">The data.</param>
        public async Task UploadDataToContainerAsync(OperationType opType, string blobName, string data)
        {
            log.LogInformation(Common.Constants.UploadDataToStorageContainerStarted);
            try
            {
                CreateCloudStroageHandler();
                var container = blobServiceClient.GetBlobContainerClient(opType == OperationType.Data ? Environment.GetEnvironmentVariable(Constants.DataContainerName) : Environment.GetEnvironmentVariable(Constants.LogContainerName));
                var blockBlob = container.GetBlockBlobClient(blobName);
                byte[] byteArray = Encoding.ASCII.GetBytes(data);
                MemoryStream stream = new MemoryStream(byteArray);
                await blockBlob.UploadAsync(stream);
                log.LogInformation(Common.Constants.UploadDataToStorageContainerCompleted);
            }
            catch (Exception ex)
            {
                log.LogError(ex.InnerException.ToString());
                throw;
            }
        }


        /// <summary>Gets the last operation details from logs asynchronous.</summary>
        /// <param name="blobName">Name of the BLOB.</param>
        /// <returns></returns>
        public async Task<OperationDetails> GetLastOperationDetailsFromLogsAsync(string blobName)
        {
            OperationDetails operationDetails = null;
            try
            {
                log.LogInformation(Common.Constants.RequestLastExecutionTime);
                CreateCloudStroageHandler();
                var container = blobServiceClient.GetBlobContainerClient(Environment.GetEnvironmentVariable(Constants.LogContainerName));
                if (await container.ExistsAsync())
                {
                    var blockBlob = container.GetBlockBlobClient(blobName);
                    if (await blockBlob.ExistsAsync())
                    {
                        var result = await blockBlob.DownloadAsync();
                        using StreamReader reader = new StreamReader(result.Value.Content);
                        string text = reader.ReadToEnd();
                        operationDetails = JsonSerializer.Deserialize<OperationDetails>(text);
                        return operationDetails;
                    }
                }
            }
            catch (Exception ex)
            {
                log.LogError(ex.InnerException.ToString());
            }
            return operationDetails;
        }

        private void CreateCloudStroageHandler()
        {
            bool.TryParse(Environment.GetEnvironmentVariable(Constants.KeyVaultEnabled), out bool isKeyVaultEnabled);
            if (isKeyVaultEnabled)
            {
                blobServiceClient = new BlobServiceClient(KeyVaultHelper.GetKeyValueAsync(Constants.StorageContainerConnectionString).Result);

            }
            else
            {
                blobServiceClient = new BlobServiceClient(Environment.GetEnvironmentVariable(Constants.StorageContainerConnectionString));
            }

            EnsureRequiredContainers();
        }

        /// <summary>Ensures the required containers.</summary>
        private async void EnsureRequiredContainers()
        {
            var container = blobServiceClient.GetBlobContainerClient(Environment.GetEnvironmentVariable(Constants.DataContainerName));
            await container.CreateIfNotExistsAsync(); //blocking call
            container = blobServiceClient.GetBlobContainerClient(Environment.GetEnvironmentVariable(Constants.LogContainerName));
            await container.CreateIfNotExistsAsync(); //blocking call
        }
    }
}
