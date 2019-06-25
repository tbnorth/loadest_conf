"""
loadest_post.py - post process (plot) LOADEST results

Terry N. Brown Brown.TerryN@epa.gov Thu 06/20/2019
"""

import argparse
import pandas as pd
from collections import defaultdict, namedtuple
from dateutil.parser import parse
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def make_parser():

    parser = argparse.ArgumentParser(
        description="""Generate plots for LOADEST output""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('obs', help="Observation (calibration) INPut file")
    parser.add_argument(
        'ind', nargs='+', help="INDividual outputs .ind output file"
    )

    return parser


def get_options(args=None):
    """
    get_options - use argparse to parse args, and return a
    argparse.Namespace, possibly with some changes / expansions /
    validatations.

    Client code should call this method with args as per sys.argv[1:],
    rather than calling make_parser() directly.

    Args:
        args ([str]): arguments to parse

    Returns:
        argparse.Namespace: options with modifications / validations
    """
    opt = make_parser().parse_args(args)

    # modifications / validations go here

    return opt


def nocomment(filename):
    """Iterate lines in file skipping '#' comment lines.

    Args:
        filename (str): file to iterate

    Returns: generator yielding strings
    """
    with open(filename) as inp:
        for line in inp:
            if not line.strip().startswith('#'):
                yield line


def get_est(filename):
    data = [i.split() for i in nocomment(filename) if i.strip()]
    while not data[0][0].startswith('---'):
        del data[0]
    del data[0]

    est = pd.DataFrame(
        data=data, columns=('date', 'time', 'flow', 'amle', 'mle', 'ladm')
    )
    for col in 'flow', 'amle', 'mle', 'ladm':
        est[col] = est[col].astype(float)
    est['datetime'] = [
        parse("%s %04d" % (i.date, int(i.time))) for i in est.itertuples()
    ]
    cf_in_cm = 35.315
    cm = est['flow'] / cf_in_cm * 24 * 3600
    for col in 'amle', 'mle', 'ladm':
        est[col + '_mgL'] = est[col] / cm * 1000
    return est


def do_plots(opt):
    """Make plots for LOADEST data

    Args:
        opt (argparse.Namespace): command line options
    """
    obs = pd.DataFrame(
        data=[i.split() for i in nocomment(opt.obs)],
        columns=('date', 'time', 'flow', 'conc'),
    )
    obs['datetime'] = [
        parse("%s %04d" % (i.date, int(i.time))) for i in obs.itertuples()
    ]
    print(obs[:5])
    for col in 'flow', 'conc':
        obs[col] = obs[col].astype(float)

    y0 = obs['conc']
    plt.scatter(obs['datetime'].values, y0, label='observed', s=0.5)

    for est_source in opt.ind:
        est = get_est(est_source)
        y1 = est['mle_mgL']
        plt.plot(est['datetime'], y1, label=est_source, lw=0.6)
    # plt.show()
    plt.legend()
    ax2 = plt.gca().twinx()
    ax2.plot(est['datetime'], est['flow'], label='flow', ls=':', c='k', lw=0.2)
    plt.gcf().set_size_inches((50, 6))
    # plt.legend()
    plt.savefig("obsest.pdf")


def main():
    opt = get_options()
    do_plots(opt)


if __name__ == "__main__":
    main()
