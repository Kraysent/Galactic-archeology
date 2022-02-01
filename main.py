import argparse
import logging

from analysis import analize
from creator import create
from integration import integrate
from omtool.datamodel import Config

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO, 
        format = '[%(levelname)s] %(asctime)s | %(message)s', 
        datefmt = '%H:%M:%S'
    )

    function_map = {
        'create': create,
        'integrate': integrate,
        'analize': analize
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode', 
        help = 'Mode of the program to run', 
        choices = function_map)
    parser.add_argument(
        'inputparams',
        help = 'input parameters for particular mode (for example, path to config file)',
        nargs = argparse.REMAINDER
    )

    args = parser.parse_args()
    func = function_map[args.mode]
    func(Config.from_yaml(args.inputparams[0]))
