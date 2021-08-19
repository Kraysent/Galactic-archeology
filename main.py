import argparse
from creator import create
from integration import integrate
from analysis import analize

parser = argparse.ArgumentParser()
parser.add_argument(
    'mode', 
    help = 'Mode of the program to run', 
    choices = ['create', 'integrate', 'analize', 'test'])
parser.add_argument(
    'datadir', 
    help = 'Directory where data is stored'
)

args = parser.parse_args()

if args.mode == 'create':
    create(args.datadir)
elif args.mode == 'integrate':
    integrate(args.datadir)
elif args.mode == 'analize':
    analize(args.datadir)
elif args.mode == 'test':
    pass
