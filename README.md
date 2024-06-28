# NESTML Server

### Install

Install NESTML and its server instance.

```
pip install nestml nestml-server
```

Note: NESTML requires NEST Simulator (>= 3.0).
To install it `conda install nest-simulator`.

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

Define path for models and/or targets:

```
export NESTML_MODELS=/tmp/nestml_models
export NESTML_TARGETS=/tmp/nestml_targets
```
