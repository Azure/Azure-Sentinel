schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "isDone": {"type": "boolean"},
        "output": {},
        "error": {"type": "string"},
        "customStatus": { 
                        "anyOf": [
                        {
                            "type": "object",
                        },{
                            "type": "string",
                        }] },
        "actions": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "functionName": {"type": "string"},
                        "actionType": {"type": "number"},
                        "input": {},
                        "retryOptions": {
                            "type": "object",
                            "properties": {
                                "firstRetryIntervalInMilliseconds": {
                                    "type": "number",
                                    "minimum": 1},
                                "maxNumberOfAttempts": {"type": "number"}
                            },
                            "required":
                                ["firstRetryIntervalInMilliseconds", "maxNumberOfAttempts"],
                            "additionalProperties": False
                        },
                        "httpRequest": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "uri": {"type": "string"},
                                "content": {},
                                "headers": {},
                                "tokenSource": {
                                    "type": "object",
                                    "properties": {
                                        "resource": {"type": "string"}
                                    },
                                    "required": ["resource"],
                                    "additionalProperties": False
                                }
                            },
                            "required":
                                ["method", "uri"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["actionType"],
                    "additionalProperties": False
                }
            }
        }
    },
    "required": ["isDone"],
    "additionalProperties": False
}
