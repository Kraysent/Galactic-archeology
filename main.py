import argparse
import logging

from amuse.lab import units

from archeology.datamodel import Config

logging.basicConfig(
    level = logging.INFO, 
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
    help = 'input parameters for particular mode (for example, input file)',
    nargs = argparse.REMAINDER
)

args = parser.parse_args()

if args.mode == 'create':
    from creator import create

    create(*args.inputparams[0:3])
elif args.mode == 'integrate':
    from integration import integrate

    integrate(Config.from_yaml(args.inputparams[0]))
elif args.mode == 'analize':
    from analysis import analize

    analize(Config.from_yaml(args.inputparams[0]))
elif args.mode == 'mananalize':
    from manual_analysis import manual_analize

    manual_analize()
