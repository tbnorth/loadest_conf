# loadest_conf

Generate [LOADEST](https://water.usgs.gov/software/loadest/) config. files from YAML.

A Python program to generate the four "FORTRAN" flavored input files
used by LOADEST.  It's easier to edit the single human friendly
[YAML file](./loadest_conf.template) than to create the
[four `.inp` files](#example_outputs) by hand, particularly for
multiple rivers with the same setup.

First, copy the template file [loadest_conf.template](./loadest_conf.template)
to a working file, e.g. `mississippi.yaml`.  The extension doesn't
matter although it could help your editor display the file nicely.
Then edit the working file and...

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

## Example outputs

```shell
python loadest_conf.py my_model_3_setup.yaml --run-name myRun
```
would create the following output files in folder `myRun`.

### `control.inp`
```
######################################################################
# control.inp created Tue Jun 18 13:44:16 2019
# for LOADEST by loadest_conf.py
# from my_model_3_setup.yaml
# for run "myRun".
######################################################################
# Header file
myRun_header.inp
# Calibration file (observations of conc.)
myRun_calib.inp
# Estimation file (flow times / levels to estimate loads)
myRun_est.inp
```   

### `myRun_header.inp`
```
######################################################################
# myRun_header.inp created Tue Jun 18 13:44:16 2019
# for LOADEST by loadest_conf.py
# from my_model_3_setup.yaml
# for run "myRun".
######################################################################
# Title
Title for LOADEST outputs
# PRTOPT estimated values print option
0
# SEOPT standard error option
1
# LDOPT, load option
0
# MODNO, model number selection
9
# NCONST, number of constituents
1
# Constituents, and UCFLAG, ULFLAG
Phosphorus                                       1    1
```   

### `myRun_est.inp`
```
######################################################################
# myRun_est.inp created Tue Jun 18 13:44:16 2019
# for LOADEST by loadest_conf.py
# from my_model_3_setup.yaml
# for run "myRun".
######################################################################
# NOBSPD, number of obs. per day
16
# date time flow
19920401 1301 270
19920401 1301 270
...
```   

### `myRun_calib.inp`
```
######################################################################
# myRun_calib.inp created Tue Jun 18 13:44:16 2019
# for LOADEST by loadest_conf.py
# from my_model_3_setup.yaml
# for run "myRun".
######################################################################
# date time flow conc(s)
19920401 1301 270 88
19920401 1701 270 88
...
```   

