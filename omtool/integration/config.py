from typing import List

import yaml
from amuse.lab import ScalarQuantity
from omtool.datamodel import yaml_loader


class LogParams:
    filename: str
    point_id: int

    @staticmethod
    def from_dict(input: dict) -> 'LogParams':
        res = LogParams()

        if 'filename' in input:
            res.filename = input['filename']
        else:
            raise Exception('No filename specified in log description')
        
        if 'point_id' in input:
            res.point_id = input['point_id']
        else:
            raise Exception('No point id specified in log description')
        
        return res
        
class IntegrationConfig:
    input_file: str
    output_file: str
    model_time: ScalarQuantity
    snapshot_interval: int
    timestep: int
    eps: ScalarQuantity
    logs: List[LogParams]

    @staticmethod
    def from_yaml(filename: str) -> 'IntegrationConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())
        
        res = IntegrationConfig()
        res.snapshot_interval = 1
        res.logs = []

        if 'input_file' in data:
            res.input_file = data['input_file']
        else:
            raise Exception('No input file specified in integration configuration file')
        
        if 'output_file' in data:
            res.output_file = data['output_file']
        else:
           raise Exception('No output file specified in integration configuration file')

        if 'model_time' in data:
            res.model_time = data['model_time']
        else:
            raise Exception('No end time specified in integration configuration file')
        
        if 'snapshot_interval' in data:
            res.snapshot_interval = data['snapshot_interval']

        if 'timestep' in data:
            res.timestep = data['timestep']
        else:
            raise Exception('No timestep specified in integration configuration file')

        if 'eps' in data:
            res.eps = data['eps']
        else:
            raise Exception('No softening distance specified in integration configuration file')

        if 'logs' in data:
            for log in data['logs']:
                res.logs.append(LogParams.from_dict(log))

        return res
