import json
d = json.load(open('C:/Code/Azure-Sentinel/Solutions/Datazag/Package/mainTemplate.json'))
def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if v == [] or v == {} or v is None:
                print(f'{path}.{k} = {v!r}')
            walk(v, f'{path}.{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f'{path}[{i}]')
walk(d)
