import requests
import json
class GitHubHelper(object):
    def __init__(self):
        github_query_url = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Hunting%20Queries/DeployedQueries.json"
        response = requests.get(github_query_url)
        response.encoding = response.apparent_encoding
        self.queries = json.loads(response.text)
    
    def get_queries(self):
        if self.queries != None:
            try:
                return [query['name'] for query in self.queries]
            except Exception as e:
                print(e)
                return None

    def get_github_query(self, query_name):
        q = None
        if self.queries != None:
            try:
                entry = [query for query in self.queries if query['name'] == query_name]
                if entry is not None:
                    q = entry[0]['query']
            except Exception as e:
                print(e)
            finally:
                return q
    