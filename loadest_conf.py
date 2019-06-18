"""
loadest_conf.py - Create LOADEST config. files from yaml source

Terry N. Brown Brown.TerryN@epa.gov 06/17/2019
"""

import os
import sys
import time

import pandas as pd
import yaml


def write_template(template, filename, **kwargs):
    """
    write_template - write output from list template

    Args:
        template (list): template
        filename (str): file to write to
        **kwargs (dict): args. for .format()
    """
    with open(filename, 'w') as out:
        out.write('\n'.join(str(i) for i in template).format(
            thisfile=os.path.basename(filename),
            **kwargs
        ))
        out.write('\n')


# YAML source file for generating LOADEST .inp files
in_file = sys.argv[1]
with open(in_file) as in_data:
    d = yaml.safe_load(in_data)
d["nconst"] = len(d["constituents"])

# for `some_run.yaml` output goes in folder `some_run`
# which must be empty
out_dir, ext = os.path.splitext(in_file)
if os.path.exists(out_dir):
    if os.listdir(out_dir):
        print("Non-empty '%s' exists, aborting" % out_dir)
        exit(10)
else:
    os.mkdir(out_dir)

# dict of filenames for the four LOADEST files
f = {"control": os.path.join(out_dir, "control.inp")}
for fn in "header", "calib", "est":
    f[fn] = os.path.join(out_dir, "%s_%s.inp" % (out_dir, fn))

# stuff common to all output files
hashes = '#' * 70
created = time.asctime()
header = [
    hashes,
    "# {thisfile} created {created}",
    "# for LOADEST by loadest_conf.py",
    "# from {source}.",
    hashes,
]
core = dict(
    base=os.path.basename(out_dir),
    source=in_file,
    created=created,
)

# the control.inp file, just lists the other three
template = [
    "# Header file",
    "{base}_header.inp",
    "# Calibration file (observations of conc.)",
    "{base}_calib.inp",
    "# Estimation file (flow times / levels to estimate loads)",
    "{base}_est.inp",
]
write_template(header+template, f["control"], **core)

# the header file, most of the setup
template = [
    "# Title",
    d["title"],
    "# PRTOPT estimated values print option",
    d["prtopt"],
    "# SEOPT standard error option",
    d["seopt"],
    "# LDOPT, load option",
    d["ldopt"],
    "# MODNO, model number selection",
    d["modno"],
    "# NCONST, number of constituents",
    d["nconst"],
    "# Constituents, and UCFLAG, ULFLAG",
]
for const in d["constituents"]:
    # 45 char. name, then 2 5 char. ints
    template.append("{c[cname]:45s}{c[ucflag]:5d}{c[ulflag]:5d}".format(
        c=const
    ))
write_template(header+template, f["header"], **core)

# how many flow observations per day?
est = pd.read_csv(d["est_file"])
daily = est.groupby("date").count()
nobs = daily["time"].values[0]

# the flow / load estimate time file
template = [
    "# NOBSPD, number of obs. per day",
    nobs,
    "# date time flow",
]
write_template(header+template, f["est"], **core)
out = open(f["est"], 'a')
for _, row in est.iterrows():
    out.write("{x[date]} {x[time]} {x[flow]}\n".format(x=row))

# the calibration / observation file
template = [
    "# date time flow conc(s)",
]
write_template(header+template, f["calib"], **core)
calib = pd.read_csv(d["calib_file"])
out = open(f["calib"], 'a')
for _, row in calib.iterrows():
    consts = [row[i['colname']] for i in d['constituents']]
    out.write(
        "{x[date]} {x[time]} {x[flow]} {conc}\n".format(
            x=row,
            conc=' '.join(str(i) for i in consts),
        ))
