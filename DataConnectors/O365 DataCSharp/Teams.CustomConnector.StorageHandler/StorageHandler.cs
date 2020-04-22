using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage;
using System;
using System.IO;
using System.Text;
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
        private CloudStorageAccount storageAccount;
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
                var myClient = storageAccount.CreateCloudBlobClient();
                var container = myClient.GetContainerReference(opType == OperationType.Data ? Environment.GetEnvironmentVariable(Constants.DataContainerName) : Environment.GetEnvironmentVariable(Constants.LogContainerName));
                var blockBlob = container.GetBlockBlobReference(blobName);
                var data = Newtonsoft.Json.JsonConvert.SerializeObject(operationDetails);
                byte[] byteArray = Encoding.ASCII.GetBytes(data);
                MemoryStream stream = new MemoryStream(byteArray);
                await blockBlob.UploadFromStreamAsync(stream);
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
                var myClient = storageAccount.CreateCloudBlobClient();
                var container = myClient.GetContainerReference(opType == OperationType.Data ? Environment.GetEnvironmentVariable(Constants.DataContainerName) : Environment.GetEnvironmentVariable(Constants.LogContainerName));
                var blockBlob = container.GetBlockBlobReference(blobName);
                byte[] byteArray = Encoding.ASCII.GetBytes(data);
                MemoryStream stream = new MemoryStream(byteArray);
                await blockBlob.UploadFromStreamAsync(stream);
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
                var myClient = storageAccount.CreateCloudBlobClient();
                var container = myClient.GetContainerReference(Environment.GetEnvironmentVariable(Constants.LogContainerName));
                if (await container.ExistsAsync())
                {
                    var blockBlob = container.GetBlockBlobReference(blobName);
                    if (await blockBlob.ExistsAsync())
                    {
                        var result = await blockBlob.DownloadTextAsync();
                        operationDetails = Newtonsoft.Json.JsonConvert.DeserializeObject<OperationDetails>(result);
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
                storageAccount = CloudStorageAccount.Parse(KeyVaultHelper.GetKeyValueAsync(Constants.StorageContainerConnectionString).Result);

            }
            else
            {
                storageAccount = CloudStorageAccount.Parse(Environment.GetEnvironmentVariable(Constants.StorageContainerConnectionString));
            }

            EnsureRequiredContainers();
        }

        /// <summary>Ensures the required containers.</summary>
        private async void EnsureRequiredContainers()
        {
            var myClient = storageAccount.CreateCloudBlobClient();
            var container = myClient.GetContainerReference(Environment.GetEnvironmentVariable(Constants.DataContainerName));
            await container.CreateIfNotExistsAsync(); //blocking call
            container = myClient.GetContainerReference(Environment.GetEnvironmentVariable(Constants.LogContainerName));
            await container.CreateIfNotExistsAsync(); //blocking call
        }
    }
}
