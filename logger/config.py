'''
Configuration objects for the logger.
'''
from typing import List


def required_get(data: dict, field: str):
    '''
    Tries to obtain the field from the dictionary and throws the
    error in case it was not found.
    '''
    try:
        return data[field]
    except KeyError as ex:
        raise Exception(
            f'No required key {field} found in logger configuration.'
        ) from ex


class HandlerConfig:
    '''
    Configuration for the handler entry.
    '''
    handler_type: str
    args: dict

    @staticmethod
    def from_dict(data: dict) -> 'HandlerConfig':
        '''
        Loads this type from dict.
        '''
        res = HandlerConfig()
        res.handler_type = required_get(data, 'handler_type')
        res.args = required_get(data, 'args')

        return res


class Config:
    '''
    General config for logger.
    '''
    handlers: List[HandlerConfig]

    @staticmethod
    def from_dict(data: dict):
        '''
        Loads this type from dict.
        '''
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
