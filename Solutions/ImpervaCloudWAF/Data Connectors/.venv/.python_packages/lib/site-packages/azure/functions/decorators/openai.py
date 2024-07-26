from typing import Optional

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
                 model: Optional[OpenAIModels] = OpenAIModels.DefaultChatModel,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.function_description = function_description
        self.function_name = function_name
        self.parameter_description_json = parameter_description_json
        self.model = model
        super().__init__(name=name, data_type=data_type)


class TextCompletionInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return TEXT_COMPLETION

    def __init__(self,
                 name: str,
                 prompt: str,
                 model: Optional[OpenAIModels] = OpenAIModels.DefaultChatModel,
                 temperature: Optional[str] = "0.5",
                 top_p: Optional[str] = None,
                 max_tokens: Optional[str] = "100",
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.prompt = prompt
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        super().__init__(name=name, data_type=data_type)


class AssistantQueryInput(InputBinding):

    @staticmethod
    def get_binding_name():
        return ASSISTANT_QUERY

    def __init__(self,
                 name: str,
                 id: str,
                 timestamp_utc: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.id = id
        self.timestamp_utc = timestamp_utc
        super().__init__(name=name, data_type=data_type)


class EmbeddingsInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EMBEDDINGS

    def __init__(self,
                 name: str,
                 input: str,
                 input_type: InputType,
                 model: Optional[str] = None,
                 max_chunk_length: Optional[int] = 8 * 1024,
                 max_overlap: Optional[int] = 128,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.input = input
        self.input_type = input_type
        self.model = model
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
                 connection_name: str,
                 collection: str,
                 query: Optional[str] = None,
                 embeddings_model: Optional[
                     OpenAIModels] = OpenAIModels.DefaultEmbeddingsModel,
                 chat_model: Optional[
                     OpenAIModels] = OpenAIModels.DefaultChatModel,
                 system_prompt: Optional[str] = semantic_search_system_prompt,
                 max_knowledge_count: Optional[int] = 1,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.connection_name = connection_name
        self.collection = collection
        self.query = query
        self.embeddings_model = embeddings_model
        self.chat_model = chat_model
        self.system_prompt = system_prompt
        self.max_knowledge_count = max_knowledge_count
        super().__init__(name=name, data_type=data_type)


class AssistantPostInput(InputBinding):

    @staticmethod
    def get_binding_name():
        return ASSISTANT_POST

    def __init__(self, name: str,
                 id: str,
                 user_message: str,
                 model: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.id = id
        self.user_message = user_message
        self.model = model
        super().__init__(name=name, data_type=data_type)


class EmbeddingsStoreOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EMBEDDINGS_STORE

    def __init__(self,
                 name: str,
                 input: str,
                 input_type: InputType,
                 connection_name: str,
                 collection: str,
                 model: Optional[
                     OpenAIModels] = OpenAIModels.DefaultEmbeddingsModel,
                 max_chunk_length: Optional[int] = 8 * 1024,
                 max_overlap: Optional[int] = 128,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.name = name
        self.input = input
        self.input_type = input_type
        self.connection_name = connection_name
        self.collection = collection
        self.model = model
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
