[![Github Python CI](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml)

# ssh-paramiko-service
A docker service used to send command to a server through ssh. Use ssh pool to avoid too many ssh connections. #ssh #service

## design
- avoid using lots of ssh connections. 5 connections in a pool.
- simple service. if TCP connection is dropped not nicely, the worker maybe drained and you need to restart the service.

## quick start
- install docker first
- then run it with docker
```bash
# on windows WSL2, or Linux, or mac
git clone https://github.com/DingXuefeng/ssh-paramiko-service.git
cd ssh-paramiko-service
docker build -t myflaskapp:1.0 .
docker run -d --name myflaskapp -p 127.0.0.1:13715:5000 -v $(readlink -f external/config.yaml):/app/external/config.yaml:ro -v $(readlink -f ~/.ssh/id_rsa):/home/john/.ssh/id_rsa:ro myflaskapp:1.0
```
- that's it! now test it:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"command": "pwd"}' http://localhost:13715/submit
```

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
### native way
```bash
python service.py
```
### docker way
```bash
docker build -t myflaskapp:1.0 .
docker run -d --name myflaskapp -p 127.0.0.1:37199:5000 -v $(readlink -f external/config.yaml):/app/external/config.yaml:ro -v $(readlink -f ~/.ssh/id_rsa):/home/john/.ssh/id_rsa:ro myflaskapp:1.0
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
