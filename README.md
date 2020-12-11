# MongoSeed

## About The Project

MongoSeed is a Python program for taking data from a seedlink server and uploading it to a MongoDB server.

## Getting Started

### Prerequisites

A python 3 environment should be setup and properly configured

### Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
python -m pip install -r requirements.txt
```

Or, if you're on Ubuntu and constantly mess up the right command like me:

```bash
pip3 install -r requirements.txt
```

## Usage

MongoSeed currently has one function: Transferring [miniSEED](https://ds.iris.edu/ds/nodes/dmc/data/formats/miniseed/) data from a [Seedlink](https://www.seiscomp.de/seiscomp3/doc/jakarta/current/apps/seedlink.html) server.

Settings should be configured in the config.json file. Hopefully the settings shouldn't be too hard to figure out.

## Liscense

Distributed under the MIT License. See ```LICENSE``` for more information.
