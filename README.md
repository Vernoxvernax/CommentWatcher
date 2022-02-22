# Nyaa-CommentsWatcher
### using the awesome self-hosted [gotify](https://github.com/gotify/server#gotifyserver).
###### DepriSheep#1841

---
Sunday-project to receive notifications, if the amount of comments on a nyaa-release has changed.

---

### Requirements:

+ git (for git clone)
+ up and running gotify container and an app-token
+ docker and docker-compose

---

### Installation:

Clone this GitHub repository:

```
$ git clone https://github.com/Vernoxvernax/Nyaa-CommentsWatcher.git
```

Build the docker image:
```
$ docker build -t depri/nyaa-commentswatcher .
```

Create the container using the `docker-compose.yml` file:
```
$ docker-compose up -d
```

Edit the `config.yml` file that has been created in the app folder.
```
$ docker-compose stop
$ vim config.yml        # "only bitches use nano 😎"
                                - **proceeds to code only in python**
```
###### If the container keeps stopping you can temporarily remove the `-d` flag to get the logs directly into you terminal. 

You can obviously run the script outside a docker container, but screens suck and crash, so this method is a lot easier to set up and manage.

---

### Notes:

+ **ONLY WORKS FOR THE FIRST PROFILE-PAGE** (nyaa's limitation for the rss feed)
+ The database is created using sqlite3 saving title, url and the amount of comments.
+ The script checks every 10 minutes.

> docker-compose.yml
```
version: '3'
services:
  nyaa-commentswatcher:
    image: depri/nyaa-commentswatcher
    container_name: nyaa-commentswatcher
    # network_mode: container:wireguard
        # OPTIONAL: To hide your IP, you can use the network of a VPN container.
    volumes:
       - ./app:/usr/src/app/app
```
Recommended VPN container: [**linuxserver/docker-wireguard**](https://github.com/linuxserver/docker-wireguard)

---

In the future, I might work on a feature to actually parse the comment to gotify, but currently I don't have much time on my hands, sorry.

... same thing for comments :)

---

### For educational purposes only!

Downloading certain sort of media from nyaa.si may not comply with your country's copyright laws.
