# NESTML Server

### Install

Install NESTML Server and its dependencies.

```
python3 -m pip install nestml-server@git+https://github.com/babsey/nestml-server

```

Note: NESTML requires NEST Simulator (>= 3.0).
To install it with this command: `conda install nest-simulator`.

### Usage

Start NESTML Server

```
nestml-server start
```

### Options

Check options in nestml-server command:

```
nestml-server
```

### Environment variables

Define HOST and/or PORT:

```
export NESTML_SERVER_HOST=http://localhost
export NESTML_SERVER_PORT=52426
```

Define path for NESTML modules:

```
export NESTML_MODULES_PATH=/tmp/nestmlmodules
```
