""" handle and save last updated time here """
from datetime import datetime
from datetime import timedelta
import logging
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError
from . import constant

logger = logging.getLogger("state_serializer")

class State:
    def __init__(self, connection_string, share_name):
        """ 
            initializes the parameters required to create file and upload and download it from fileshare 
        """

        self.share_cli = ShareClient.from_connection_string(conn_str=connection_string, share_name=share_name)
        self.file_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=constant.FILE_LAST_POLL_TIME)
        self.file_event_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=constant.FILE_LAST_EVENT_NUMBER)
        self.file_triage_items_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=constant.FILE_LAST_TRIAGE_ITEMS)

    def post(self, marker_text: str):
        """ 
            posts the new time to azure file share file, 
            from which it will poll next time
        """
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        """ 
        gets the last polled time from azure file share 
        """
        
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

    def post_event(self, marker_text: int):
        """ 
            posts the new time to azure file share file, 
            from which it will poll next time
        """
        logger.info(str(marker_text) + " event number stored now")
        try:
            self.file_event_cli.upload_file(str(marker_text))
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_event_cli.upload_file(str(marker_text))

    def get_event(self):
        """ 
        gets the last polled time from azure file share 
        """
        
        try:
            return self.file_event_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

    def get_last_polled_time(self, historical_days):
        """ 
            gets the last updated time,
            for historical poll takes user input value or default value of 10 days
        """

        try:
            day = int(historical_days)
        except Exception:
            day = constant.DAYS
        current_time = datetime.utcnow() - timedelta(minutes=constant.MINUTE)
        past_time = self.get()
        if past_time is not None:
            logger.info("The last time point is: {}".format(past_time))
        else:
            logger.info("There is no last time point, trying to get events from last " + str(day) + " days.")
            past_time = (current_time - timedelta(days=day)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.post(current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        return (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))

    def get_last_event(self, historical_days):
        """
            gets the event number from which last polled
        """
        event = None
        try:
            event = int(self.get_event())
        except Exception:
            event = self.get_last_polled_time(historical_days)

        return event
    
    def post_triage_items(self, marker_text: str):
        """ 
            posts the unique triage items to a file from which it will fetch only
            150 items in next poll
        """
        try:
            logger.info('post triage items:')
            self.file_triage_items_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            logger.info('triage file does not exist create one:')
            self.share_cli.create_share()
            self.file_triage_items_cli.upload_file(marker_text)

    def get_triage_items(self):
        """ 
        gets the last unique triage items list from azure file share 
        """
        
        try:
            logger.info('fetch triage item file:')
            return self.file_triage_items_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            logger.info('triage item file does not exist')
            return None
        


        



    
