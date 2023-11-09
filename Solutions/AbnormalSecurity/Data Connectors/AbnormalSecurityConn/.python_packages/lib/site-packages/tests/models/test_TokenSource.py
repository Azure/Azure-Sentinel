from azure.durable_functions.models.TokenSource import ManagedIdentityTokenSource

def test_serialization_fields():
    """Validates the TokenSource contains the expected fields when serialized to JSON"""
    token_source = ManagedIdentityTokenSource(resource="TOKEN_SOURCE")
    token_source_json = token_source.to_json()

    # Output JSON should contain a resource field and a kind field set to `AzureManagedIdentity`
    assert "resource" in token_source_json.keys()
    assert "kind" in token_source_json.keys()
    assert token_source_json["kind"] == "AzureManagedIdentity"