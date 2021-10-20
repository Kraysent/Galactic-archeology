import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    'mode', 
    help = 'Mode of the program to run', 
    choices = ['create', 'integrate', 'analize', 'mananalize', 'test'])
parser.add_argument(
    'datadir', 
    help = 'Directory where data is stored'
)

args = parser.parse_args()

if args.mode == 'create':
    from creator import create

    create(args.datadir)
elif args.mode == 'integrate':
    from integration import integrate

    integrate(args.datadir)
elif args.mode == 'analize':
    from analysis import analize

    analize(args.datadir)
elif args.mode == 'mananalize':
    from manual_analysis import manual_analize

    manual_analize()
elif args.mode == 'test':
    pass
