'''
General config for logger.
'''

class Config:
    '''
    General config for logger.
    '''
    filename: str

    @staticmethod
    def from_dict(data: dict):
        '''
        Loads this type from dict.
        '''
        res = Config()
        res.filename = data.get('filename', '')

        return res