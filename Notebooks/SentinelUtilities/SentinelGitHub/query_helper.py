import json
class QueryHelper(object):
    
    def get_query_for_hunting_bookmark(start_date, end_date, max_record=20):
        return 'HuntingBookmark | where EventTime > datetime("{}") and EventTime <= datetime("{}") | take {}'.format(start_date, end_date, max_record)
