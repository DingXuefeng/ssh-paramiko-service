[![Python CI](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml)

# ssh-paramiko-service
A docker service used to send command to a server through ssh. Use ssh pool to avoid too many ssh connections. #ssh #service

## design
- avoid using lots of ssh connections. 5 connections in a pool.
- simple service. if TCP connection is dropped not nicely, the worker maybe drained and you need to restart the service.

## How to install
- Use [mini-conda](https://docs.conda.io/en/latest/miniconda.html) to manage your virtual env.
```bash
conda create -n ssh-paramiko-service
conda activate ssh-paramiko-service
conda install pip
git clone https://github.com/DingXuefeng/ssh-paramiko-service.git
cd ssh-paramiko-service
pip install -r requirements.txt
```

## How to configure
- create a file `ssh-paramiko-service/external/config.yaml`. The name of the file is hard coded, see [`service.py`](service.py)

- Put in the file your server name etc. example file:
```yaml
num_workers: 5
max_connections: 1
server:
  host: linux.server.com
  user: john
  pkey: /home/john/.ssh/id_rsa
```

## How to launch the service?
```bash
python service.py
```

## How to test the service?
### Use test/dev.ipynb
- run the cell with `import requests` etc.
### Use `curl` command
```bash
curl -X POST -H "Content-Type: application/json" -d '{"command": "date"}' http://localhost:5000/submit
```
You should see something like
```
{"error":"","output":"Tue Apr 25 19:24:16 CST 2023\n"}
```
### Use unittest and test/dev.ipynb
- run the cell with `unittest.TextTestRunner().run(suite)`

## How to UnitTest (without connecting to ssh server)
### Use `python -m test`
```bash
python -m unittest discover test
```
