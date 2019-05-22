# HVO-API
---
HVO-API is a companion application for the [vsc-vdx](https://github.com/usgs/vsc-vdx) project. The idea is to be able to extract JSON data from VDX databases (and a few other random sources) using easily constructable URLs. Initially written as a way to learn the datasets in use at HVO, it's been continually expanded as users have requested access to different data.

## Requirements
---
At a high level, you'd need the following to get any use out of this codebase:
1. Python 3 and the packages listed in requirements.txt
2. A webserver that can run python apps
3. Some data to fetch. Note that VDX databases aren't explicitly required, but the code does expect the tables to have specific fields.

## Currently Supported Datasets
---
* Ash
* EDXRF
* Files (from a files directory defined in the config file)
* Flyspec Array Data
* GPS
* Hypocenters
* Lava level (Measurements taken with a Sick DT1000 sensor)
* Lava level (Old method)
* Logs (This is probably specific to VSC)
* NPSAdvisory
* RSAM
* RTNet
* SO2Emissions
* SO2HighRes
* Strain
* Tilt
* Tremor
* Triggers