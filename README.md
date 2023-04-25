# ssh-paramiko-service
A docker service used to send command to a server through ssh. Use ssh pool to avoid too many ssh connections. #ssh #service

## design
- avoid using lots of ssh connections. 5 connections in a pool.
- simple service. if TCP connection is dropped not nicely, the worker maybe drained and you need to restart the service.
