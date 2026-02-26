from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceExistsError
import base64
import logging


class StateManager:
    def __init__(self, connection_string, share_name='funcstatemarkershare', file_path='funcstatemarkerfile'):
        logging.getLogger().setLevel(logging.WARNING)
        self.share_cli = ShareClient.from_connection_string(conn_str=connection_string, share_name=share_name)
        self.file_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=file_path)
        logging.getLogger().setLevel(logging.INFO)

    def post(self, marker_text: str):
        logging.getLogger().setLevel(logging.WARNING)
        try:
            self.file_cli.upload_file(marker_text)
            logging.getLogger().setLevel(logging.INFO)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)
            logging.getLogger().setLevel(logging.INFO)

    def get(self):
        logging.getLogger().setLevel(logging.WARNING)
        try:
            results =  self.file_cli.download_file().readall().decode()
            logging.getLogger().setLevel(logging.INFO)
            return results
        except ResourceNotFoundError:
            logging.getLogger().setLevel(logging.INFO)
            return None
            

class AzureStorageQueueHelper:
    def __init__(self,connectionString,queueName):
        logging.getLogger().setLevel(logging.WARNING)
        self.__service_client = QueueServiceClient.from_connection_string(conn_str=connectionString)
        self.__queue = self.__service_client.get_queue_client(queueName)
        try:
            self.__queue.create_queue()
        except ResourceExistsError:
            # Resource exists
            pass
        logging.getLogger().setLevel(logging.INFO)
    
    # Helper function to encode message in base64
    def base64Encoded(self,message):
        messageString = str(message)
        message_bytes = messageString.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    # This method is used to read messages from the queue. 
    # This will pop the message from the queue (deque operation)
    def deque_from_queue(self):
        logging.getLogger().setLevel(logging.WARNING)
        message = self.__queue.receive_message()
        logging.getLogger().setLevel(logging.INFO)
        return message

    # This method send data into the queue
    def send_to_queue(self, message, encoded):
        logging.getLogger().setLevel(logging.WARNING)
        if encoded:
            self.__queue.send_message(self.base64Encoded(message))
        else:
            self.__queue.send_message(message)
        logging.getLogger().setLevel(logging.INFO)
    
    # This method deletes the message based on messageId
    def delete_queue_message(self, messageId, popReceipt):
        logging.getLogger().setLevel(logging.WARNING)
        self.__queue.delete_message(messageId,popReceipt)
        logging.getLogger().setLevel(logging.INFO)

    # This method reads an approximate count of messages in the queue
    def get_queue_current_count(self):
        logging.getLogger().setLevel(logging.WARNING)
        properties = self.__queue.get_queue_properties()
        logging.getLogger().setLevel(logging.INFO)
        return properties.approximate_message_count