# Python_Email_Notification

POC Sending email notification when the server is down

### Project structure
  
* requirements.txt  
* environment.yml  
* python script  

```
├── email_sender.py
├── environment.yml
├── README.md
└── requirements.txt
```

### Env Variables

* sender email address  
* recipient address  
* smtp server 


### Docker setup

Create a docker service with tree nodes. The requests will be answered the proxy.  
Make the the http port available.  

```
docker swam init .
(docker join swarm?)
docker service create -p 8088:80 --name web nginx:1.13.7
docker service update -publish-add 8080:80
```
### Docker cmds

```
docker service ps web
docker service ls
docker network inspect # swarm network created should have a swarm scope
```

