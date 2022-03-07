from typing import List


def required_get(data: dict, field: str):
    try:
        return data[field]
    except KeyError as e:
        raise Exception(f'No required key {field} found in logger configuration.') from e

class HandlerConfig:
    handler_type: str
    args: dict

    @staticmethod
    def from_dict(data: dict) -> 'HandlerConfig':
        res = HandlerConfig()
        res.handler_type = required_get(data, 'handler_type')
        res.args = required_get(data, 'args')

        return res

class Config:
    handlers: List[HandlerConfig]
    
    @staticmethod
    def from_dict(data: dict):
        res = Config()
        res.handlers = [
            HandlerConfig.from_dict(handler) for handler in data.get('handlers', [
            { 
                'handler_type': 'console',
                'args': {
                    'format': '[%(levelname)s] %(asctime)s | %(message)s'
                }
            }
        ])]

        return res
