import argparse
import atexit
import logging

from analysis import analize
from creator import create
from integration import integrate
from omtool.analysis import AnalysisConfig
from omtool.creation import CreationConfig
from omtool.datamodel import ProfilerSingleton
from omtool.integration import IntegrationConfig

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.DEBUG, 
        format = '[%(levelname)s] %(asctime)s | %(message)s', 
        datefmt = '%H:%M:%S'
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode', 
        help = 'Mode of the program to run', 
        choices = ['create', 'integrate', 'analize', 'mananalize', 'test'])
    parser.add_argument(
        'inputparams',
        help = 'input parameters for particular mode (for example, path to config file)',
        nargs = argparse.REMAINDER
    )

    args = parser.parse_args()

    @atexit.register
    def print_times():
        profiler_instance = ProfilerSingleton.get_instance()
        res = profiler_instance.dump_times()

        for key, val in res.items():
            logging.info(f'{key} worked {val:.02f} seconds on average')

    if args.mode == 'create':
        create(CreationConfig.from_yaml(args.inputparams[0]))
    elif args.mode == 'integrate':
        integrate(IntegrationConfig.from_yaml(args.inputparams[0]))
    elif args.mode == 'analize':
        analize(AnalysisConfig.from_yaml(args.inputparams[0]))
