[![Github Python CI](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DingXuefeng/ssh-paramiko-service/actions/workflows/ci.yml)

# ssh-paramiko-service
A docker service used to send command to a server through ssh. Use ssh pool to avoid too many ssh connections. #ssh #service

## design
- avoid using lots of ssh connections. 5 connections in a pool.
- simple service. if TCP connection is dropped not nicely, the worker maybe drained and you need to restart the service.

## Quick start
- install docker first
- write a config file `ssh-paramiko-service/external/config.yaml` (see **How to configure**)
- then run it with docker
```bash
# on windows WSL2, or Linux, or mac
git clone https://github.com/DingXuefeng/ssh-paramiko-service.git
cd ssh-paramiko-service
docker compose up
```
- that's it! now test it:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"command": "pwd"}' http://localhost:5000/submit
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

- Put in the file your server name, user name for login to ssh etc.
- example file:
```yaml
num_workers: 5
max_connections: 1
server:
  host: linux.server.com
  user: john
  pkey: /home/john/.ssh/id_rsa
  # if your private key is password protected, uncomment this line:
  # pkey_password: "my@key+p@ssw0rd"
  # if you need to jump over some bastion node, uncomment this line:
  # ProxyCommand: "ssh john@bastion nc {HOST} {PORT}"
```
- here `/home/john/.ssh/id_rsa` should be the location of your ssh key.

- create a file `ssh-paramiko-service/.env`. The name of the file is special and `docker compose` will only read from this file.
- Put in the file a few things:
```bash
CONFIGFILE=./external/config.yaml
SSH_KEY=/home/john/.ssh/id_rsa
SSH_KEY_IN_CONTAINER=/home/john/.ssh/id_rsa
```
- You'd better set `pkey`, `SSH_KEY`, `SSH_KEY_IN_CONTAINER` all the same.

## How to launch the service?
### native way
```bash
python service.py
```
### docker way
```bash
docker build -t myflaskapp:1.0 .
docker run -d --name myflaskapp -p 127.0.0.1:5000:5000 -v $(readlink -f external/config.yaml):/app/external/config.yaml:ro -v $(readlink -f ~/.ssh/id_rsa):/home/john/.ssh/id_rsa:ro myflaskapp:1.0
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
