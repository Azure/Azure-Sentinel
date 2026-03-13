import typing

from . import meta


class MCPToolTriggerConverter(meta.InConverter, binding='mcpToolTrigger',
                              trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, dict, bytes))

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        """
        Decode incoming MCP tool request data.
        Returns the raw data in its native format (string, dict, bytes).
        """
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, use the value directly
            return data.value
        elif data.type == 'string':
            # If it's a string, use it as-is
            return data.value
        elif data.type == 'bytes':
            return data.value
        else:
            # Fallback to python_value for other types
            return data.python_value if hasattr(data, 'python_value') else data.value

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type] = None):
        """
        Encode the return value from MCP tool functions.
        MCP tools typically return string responses.
        """
        if obj is None:
            return meta.Datum(type='string', value='')
        elif isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        else:
            # Convert other types to string
            return meta.Datum(type='string', value=str(obj))
