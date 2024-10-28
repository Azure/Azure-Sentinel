import unittest
from SentinelFunctionsOrchestrator.soar_connector_async import AbnormalSoarConnectorAsync
from copy import deepcopy

DUMMY_API_KEY = "DUMMY_API_KEY"
NUM_CONSUMERS = 0

class TestAbnormalSoarConnectorAsync(unittest.TestCase):

    threat_resp = {
        "threatId": "40080400-6300-9600-f800-afb76fd00000",
        "messages": [
            {
                "abxMessageId": 4670020130001212344,
                "receivedTime": "2024-05-07T08:09:00Z",
                "remediationTimestamp": "2024-05-07T08:09:03.183578Z"
            },
            {
                "abxMessageId": 4670020130001212345,
                "receivedTime": "2024-05-07T08:09:00Z",
                "remediationTimestamp": "2024-05-07T08:10:03.183578Z"
            },
            {
                "abxMessageId": 4670020130001212346,
                "receivedTime": "2024-05-07T08:09:00Z",
                "remediationTimestamp": "2024-05-07T08:15:03.183578Z"
            }
        ]
    }

    context = {
        "gte_datetime": "2024-05-07T08:10:00Z",
        "lte_datetime": "2024-05-07T08:15:00Z"
    }

    def test_wrong_time_format_in_context(self):
        # Initialize values
        threat_response = deepcopy(self.threat_resp)
        context = deepcopy(self.context)
        connector = AbnormalSoarConnectorAsync(DUMMY_API_KEY, NUM_CONSUMERS)
        
        # Override values
        context["lte_datetime"] = "2024-05-0708:15:00Z"

        result = connector._extract_messages(context, threat_response)
        self.assertEqual(len(result), 0)

    def test_wrong_time_format_in_remediation_timestamp(self):
        # Initialize values
        threat_response = deepcopy(self.threat_resp)
        context = deepcopy(self.context)
        connector = AbnormalSoarConnectorAsync(DUMMY_API_KEY, NUM_CONSUMERS)
        
        # Override values
        threat_response["messages"][1]["remediationTimestamp"] = "2024-05-07T08:10:03Z"

        result = connector._extract_messages(context, threat_response)
        self.assertEqual(len(result), 0)

    def test_correct_flow_with_one_filtered_message(self):
        # Initialize values
        threat_response = deepcopy(self.threat_resp)
        context = deepcopy(self.context)
        connector = AbnormalSoarConnectorAsync(DUMMY_API_KEY, NUM_CONSUMERS)
        
        result = connector._extract_messages(context, threat_response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["abxMessageId"], 4670020130001212345)

    def test_correct_flow_with_two_filtered_message(self):
        # Initialize values
        threat_response = deepcopy(self.threat_resp)
        context = deepcopy(self.context)
        connector = AbnormalSoarConnectorAsync(DUMMY_API_KEY, NUM_CONSUMERS)

        context = {
            "gte_datetime": "2024-05-07T08:09:00Z",
            "lte_datetime": "2024-05-07T08:15:00Z"
        }
        
        result = connector._extract_messages(context, threat_response)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["abxMessageId"], 4670020130001212344)
        self.assertEqual(result[1]["abxMessageId"], 4670020130001212345)
        
    def test_correct_flow_with_three_filtered_message(self):
        # Initialize values
        threat_response = deepcopy(self.threat_resp)
        context = deepcopy(self.context)
        connector = AbnormalSoarConnectorAsync(DUMMY_API_KEY, NUM_CONSUMERS)

        context = {
            "gte_datetime": "2024-05-07T08:09:00Z",
            "lte_datetime": "2024-05-07T08:16:00Z"
        }
        
        result = connector._extract_messages(context, threat_response)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["abxMessageId"], 4670020130001212344)
        self.assertEqual(result[1]["abxMessageId"], 4670020130001212345)
        self.assertEqual(result[2]["abxMessageId"], 4670020130001212346)




    