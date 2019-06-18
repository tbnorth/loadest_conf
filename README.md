# loadest_conf

Generate [LOADEST](https://water.usgs.gov/software/loadest/) config. files from YAML.

A Python program to generate the four "FORTRAN" flavored input files
used by LOADEST.

```shell
python loadest_conf.py mississippi.yaml
```
would create:
```
mississippi/
    control.inp
    mississippi_header.inp
    mississippi_est.inp
    mississippi_calib.inp
```
using the Mississippi inputs referenced in `mississippi.yaml`, whereas
```shell
python loadest_conf.py mississippi.yaml --run-name nile \
  --est-file nileflow.csv --calib-file nileobs.csv
```
would create   
```
nile/
    control.inp
    nile_header.inp
    nile_est.inp
    nile_calib.inp
```
using the Nile inputs listed on the command line. The rest of the setup
would be taken from `mississippi.yaml`.

## Usage

```
usage: loadest_conf.py [-h] [--run-name NAME] [--est-file CSVFILE]
                       [--calib-file CSVFILE]
                       CONFFILE

Generate input files for LOADEST

positional arguments:
  CONFFILE              Configuration file in YAML format

optional arguments:
  -h, --help            show this help message and exit
  --run-name NAME       Base name to use for run / outputs folder
  --est-file CSVFILE    "Estimates" file, flows at times when loads are wanted
  --calib-file CSVFILE  Calibration file, observations of concentrations
```

## To do

 - handle date format changes etc. as needed, field names etc.
 - interpolate flow data when conc. data has no associated flow?
 - post process output
    - plot obs. vs. model
 - support model number 99 (custom model)
 - support user defined seasons (reporting)
 - support user defined periods (multiple fittings?)

