import yaml
from omtool.datamodel import required_get, yaml_loader


class LogParams:
    @staticmethod
    def from_dict(input: dict) -> 'LogParams':
        res = LogParams()
        res.filename = required_get(input, 'filename')
        res.point_id = required_get(input, 'point_id')
        
        return res
        
class IntegrationConfig:
    @staticmethod
    def from_yaml(filename: str) -> 'IntegrationConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        return IntegrationConfig.from_dict(data)

    @staticmethod
    def from_dict(input: dict) -> 'IntegrationConfig':
        res = IntegrationConfig()
        res.input_file = required_get(input, 'input_file')
        res.output_file = required_get(input, 'output_file')
        res.overwrite = input.get('overwrite', False)
        res.model_time = required_get(input, 'model_time')
        res.snapshot_interval = input.get('snapshot_interval', 1)
        res.timestep = required_get(input, 'timestep')
        res.eps = required_get(input, 'eps')
        res.logs = [
            LogParams.from_dict(log) for log in input.get('logs', [])
        ]
        
        return res
