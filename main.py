import argparse

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

    integrate(*args.inputparams[0:2])
elif args.mode == 'analize':
    from analysis import analize

    analize(*args.inputparams[0:2])
elif args.mode == 'mananalize':
    from manual_analysis import manual_analize

    manual_analize()
elif args.mode == 'test':
    pass
