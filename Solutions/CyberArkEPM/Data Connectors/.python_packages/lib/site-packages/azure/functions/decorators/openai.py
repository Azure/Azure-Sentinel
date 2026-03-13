from typing import Optional, Union

from azure.functions.decorators.constants import (ASSISTANT_SKILL_TRIGGER,
                                                  TEXT_COMPLETION,
                                                  ASSISTANT_QUERY,
                                                  EMBEDDINGS, EMBEDDINGS_STORE,
                                                  ASSISTANT_CREATE,
                                                  ASSISTANT_POST,
                                                  SEMANTIC_SEARCH)
from azure.functions.decorators.core import Trigger, DataType, InputBinding, \
    OutputBinding
from azure.functions.decorators.utils import StringifyEnum


class InputType(StringifyEnum):

    RawText = "raw_text",
    FilePath = "file_path"


class OpenAIModels(StringifyEnum):
    DefaultChatModel = "gpt-3.5-turbo"
    DefaultEmbeddingsModel = "text-embedding-ada-002"


class AssistantSkillTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return ASSISTANT_SKILL_TRIGGER

    def __init__(self,
                 name: str,
                 function_description: str,
                 function_name: Optional[str] = None,
                 parameter_description_json: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.function_description = function_description
        self.function_name = function_name
        self.parameter_description_json = parameter_description_json
        super().__init__(name=name, data_type=data_type)


class TextCompletionInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return TEXT_COMPLETION

    def __init__(self,
                 name: str,
                 prompt: str,
                 ai_connection_name: Optional[str] = "",
                 chat_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultChatModel,
                 temperature: Optional[str] = "0.5",
                 top_p: Optional[str] = None,
                 max_tokens: Optional[str] = "100",
                 is_reasoning_model: Optional[bool] = False,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.prompt = prompt
        self.ai_connection_name = ai_connection_name
        self.chat_model = chat_model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.is_reasoning_model = is_reasoning_model
        super().__init__(name=name, data_type=data_type)


class AssistantQueryInput(InputBinding):

    @staticmethod
    def get_binding_name():
        return ASSISTANT_QUERY

    def __init__(self,
                 name: str,
                 id: str,
                 timestamp_utc: str,
                 chat_storage_connection_setting: Optional[str] = "AzureWebJobsStorage",        # noqa: E501
                 collection_name: Optional[str] = "ChatState",
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.id = id
        self.timestamp_utc = timestamp_utc
        self.chat_storage_connection_setting = chat_storage_connection_setting
        self.collection_name = collection_name
        super().__init__(name=name, data_type=data_type)


class EmbeddingsInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EMBEDDINGS

    def __init__(self,
                 name: str,
                 input: str,
                 input_type: InputType,
                 ai_connection_name: Optional[str] = "",
                 embeddings_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultEmbeddingsModel,
                 max_chunk_length: Optional[int] = 8 * 1024,
                 max_overlap: Optional[int] = 128,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.input = input
        self.input_type = input_type
        self.ai_connection_name = ai_connection_name
        self.embeddings_model = embeddings_model
        self.max_chunk_length = max_chunk_length
        self.max_overlap = max_overlap
        super().__init__(name=name, data_type=data_type)


semantic_search_system_prompt = \
    """You are a helpful assistant. You are responding to requests
    from a user about internal emails and documents. You can and
    should refer to the internal documents to help respond to
    requests. If a user makes a request that's not covered by the
    internal emails and documents, explain that you don't know the
    answer or that you don't have access to the information.

    The following is a list of documents that you can refer to when
    answering questions. The documents are in the format
    [filename]: [text] and are separated by newlines. If you answer
    a question by referencing any of the documents, please cite the
    document in your answer. For example, if you answer a question
    by referencing info.txt, you should add "Reference: info.txt"
    to the end of your answer on a separate line."""


class SemanticSearchInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return SEMANTIC_SEARCH

    def __init__(self,
                 name: str,
                 search_connection_name: str,
                 collection: str,
                 query: Optional[str] = None,
                 ai_connection_name: Optional[str] = "",
                 embeddings_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultEmbeddingsModel,
                 chat_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultChatModel,
                 system_prompt: Optional[str] = semantic_search_system_prompt,
                 max_knowledge_count: Optional[int] = 1,
                 temperature: Optional[str] = "0.5",
                 top_p: Optional[str] = None,
                 max_tokens: Optional[str] = "100",
                 is_reasoning_model: Optional[bool] = False,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.search_connection_name = search_connection_name
        self.collection = collection
        self.query = query
        self.ai_connection_name = ai_connection_name
        self.embeddings_model = embeddings_model
        self.chat_model = chat_model
        self.system_prompt = system_prompt
        self.max_knowledge_count = max_knowledge_count
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.is_reasoning_model = is_reasoning_model
        super().__init__(name=name, data_type=data_type)


class AssistantPostInput(InputBinding):

    @staticmethod
    def get_binding_name():
        return ASSISTANT_POST

    def __init__(self, name: str,
                 id: str,
                 user_message: str,
                 ai_connection_name: Optional[str] = "",
                 chat_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultChatModel,
                 chat_storage_connection_setting: Optional[str] = "AzureWebJobsStorage",       # noqa: E501
                 collection_name: Optional[str] = "ChatState",
                 temperature: Optional[str] = "0.5",
                 top_p: Optional[str] = None,
                 max_tokens: Optional[str] = "100",
                 is_reasoning_model: Optional[bool] = False,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.id = id
        self.user_message = user_message
        self.ai_connection_name = ai_connection_name
        self.chat_model = chat_model
        self.chat_storage_connection_setting = chat_storage_connection_setting
        self.collection_name = collection_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.is_reasoning_model = is_reasoning_model
        super().__init__(name=name, data_type=data_type)


class EmbeddingsStoreOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EMBEDDINGS_STORE

    def __init__(self,
                 name: str,
                 input: str,
                 input_type: InputType,
                 store_connection_name: str,
                 collection: str,
                 ai_connection_name: Optional[str] = "",
                 embeddings_model: Optional
                 [Union[str, OpenAIModels]]
                 = OpenAIModels.DefaultEmbeddingsModel,
                 max_chunk_length: Optional[int] = 8 * 1024,
                 max_overlap: Optional[int] = 128,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.input = input
        self.input_type = input_type
        self.store_connection_name = store_connection_name
        self.collection = collection
        self.ai_connection_name = ai_connection_name
        self.embeddings_model = embeddings_model
        self.max_chunk_length = max_chunk_length
        self.max_overlap = max_overlap
        super().__init__(name=name, data_type=data_type)


class AssistantCreateOutput(OutputBinding):

    @staticmethod
    def get_binding_name():
        return ASSISTANT_CREATE

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        super().__init__(name=name, data_type=data_type)
