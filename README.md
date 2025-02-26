# AIP Scheduling
This is a repository for the package that solves the scheduling problem 
of the AIP 2025 conference.

Given an input table descring the minisymposiums to be scheduled, we
return three tables.


## Repository guide
- [docs](docs): Hosts documentation (in addition to readme files and docstrings)
  of the project.
- [aip_scheduling](aip_scheduling): Contains the Python package that solves the 
  problem.
  It contains scripts that define the input and the output data schemas, the 
  solution engine, and other auxiliary modules.
- [test_aip_scheduling](aip_scheduling): Hosts testing suits and testing data 
  sets used for testing the solution throughout the development process.
- `pyproject.toml` is used to build the distribution files 
  of the package (more information [here](https://github.com/mipwise/mip-go/blob/main/6_deploy/1_distribution_package/README.md)).

## Setting Up and Using the package

This project is managed by uv, a python package installer.
You can create the virtual enviroment that is able to run the package using the command `uv sync`