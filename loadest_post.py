"""
loadest_post.py - post process (plot) LOADEST results

Terry N. Brown Brown.TerryN@epa.gov Thu 06/20/2019
"""

import argparse
import pandas as pd
from dateutil.parser import parse
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
from light_orm import light_orm as lo
from itertools import zip_longest

register_matplotlib_converters()

DB_SQL = [
    """create table est (
    site int,
    date date,
    flow real,
    conc real
    )""",
    """create table obs (
    site int,
    date date,
    flow real,
    conc real
    )""",
    """create table site (
    site serial,
    name text,
    lat real,
    lon real
    )""",
    """create index obs_date_idx on obs(date)""",
    """create index est_date_idx on est(date)""",
    """create index obs_site_idx on obs(site)""",
    """create index est_site_idx on est(site)""",
    """create index site_site_idx on site(site)""",
]


def make_parser():

    parser = argparse.ArgumentParser(
        description="""Generate plots for LOADEST output""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('obs', help="Observation (calibration) INPut file")
    parser.add_argument(
        'ind', nargs='+', help="INDividual outputs .ind output file"
    )
    parser.add_argument('--db', help="DB for storing site data")
    parser.add_argument('--site', help="site name for storing site data")

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
    """read data from estimation file"""
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
    if opt.site:
        con, cur = lo.get_con_cur(opt.db, DB_SQL)
        site, new = lo.get_or_make_pk(cur, 'site', {'name': opt.site})
        con.commit()

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
    if opt.site:
        cur.executemany(
            "insert into obs (site, date, flow, conc) values (%s,%s,%s,%s)",
            zip_longest(
                [],
                [i.strftime("%Y-%m-%d") for i in obs['datetime']],
                obs['flow'],
                y0,
                fillvalue=site,
            ),
        )
        con.commit()

    for est_source in opt.ind:
        est = get_est(est_source)
        y1 = est['mle_mgL']
        plt.plot(est['datetime'], y1, label=est_source, lw=0.6)
        if opt.site:
            cur.executemany(
                "insert into est (site, date, flow, conc) values (%s,%s,%s,%s)",
                zip_longest(
                    [],
                    [i.strftime("%Y-%m-%d") for i in est['datetime']],
                    est['flow'],
                    y1,
                    fillvalue=site,
                ),
            )
            con.commit()
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
