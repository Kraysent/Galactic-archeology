import yaml
from omtool.datamodel import required_get, yaml_loader
import io_service

class LogParams:
    @staticmethod
    def from_dict(data: dict) -> 'LogParams':
        res = LogParams()
        res.filename = required_get(data, 'filename')
        res.point_id = required_get(data, 'point_id')
        
        return res
        
class IntegrationConfig:
    @staticmethod
    def from_yaml(filename: str) -> 'IntegrationConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        return IntegrationConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> 'IntegrationConfig':
        res = IntegrationConfig()
        res.input_file = io_service.Config.from_dict(required_get(data, 'input_file'))
        res.output_file = required_get(data, 'output_file')
        res.overwrite = data.get('overwrite', False)
        res.model_time = required_get(data, 'model_time')
        res.snapshot_interval = data.get('snapshot_interval', 1)
        res.timestep = required_get(data, 'timestep')
        res.eps = required_get(data, 'eps')
        res.logs = [
            LogParams.from_dict(log) for log in data.get('logs', [])
        ]
        
        return res
