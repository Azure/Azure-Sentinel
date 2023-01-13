import jwt


def get_clp_id(token):
    return jwt.decode(token, options={"verify_signature": False}).get('cid')


def find_token_by_clp(clp_id, api_tokens):
    return next(filter(lambda token: get_clp_id(token) == clp_id, api_tokens), None)
