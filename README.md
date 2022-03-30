# NESTML Server

### Install

Install NEST Simulator into home folder because of non-root permission
to write files into nest install directory.

```
wget https://github.com/nest/nest-simulator/archive/refs/heads/master.zip -O /tmp/nest-simulator-master.zip
unzip /tmp/nest-simulator-master.zip -d /tmp/
rm -rf /tmp/nest-build/; mkdir -p /tmp/nest-build; cd /tmp/nest-build
cmake -DCMAKE_INSTALL_PREFIX:PATH=$HOME/opt/nest-nestml /tmp/nest-simulator-master
make -j $(nproc)
make install
```

### Singularity

Use singularity or install all requirements in host.

Build Singularity images with all requirements for NESTML and server
```
sudo singularity build nestml-server.sif singularity/nest-server.def
```

Use Singularity for NESTML Server and Jupyter notebook
```
singularity shell nestml-server.sif
```


### Usage

##### Start NESTML Server

```
gunicorn nestml_server:app --bind 0.0.0.0:5005 --timeout 120
```

##### Start Jupyter notebook

User can send code to NESTML server to build and install NESTML models.

```
cd examples/notebook
jupyter notebook
```
