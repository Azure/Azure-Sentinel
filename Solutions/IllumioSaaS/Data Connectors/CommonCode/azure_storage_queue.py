import logging
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceExistsError
import base64

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
        message = self.__queue.receive_message()
        return message

    # This method send data into the queue
    def send_to_queue(self, message, encoded):
        if encoded:
            self.__queue.send_message(self.base64Encoded(message))
        else:
            self.__queue.send_message(message)
    
    # This method deletes the message based on messageId
    def delete_queue_message(self, messageId, popReceipt):
        self.__queue.delete_message(messageId, popReceipt)

    # This method reads an approximate count of messages in the queue
    def get_queue_current_count(self):
        properties = self.__queue.get_queue_properties()
        return properties.approximate_message_count