# duplicati-discord-notification

https://duplicati-notifications.lloyd.ws/
Blog Post
https://james.lloyd.ws/duplicati-discord-notifications/
## Docker

```
docker pull jameslloyd/duplicati-discord-notification
docker run -p 8991:5000  --name duplicati-notifications  jameslloyd/duplicati-notifications
```
## docker-compose
```
---
version: "2.1"
services:
  duplicati-notifications:
    image: jameslloyd/duplicati-notifications
    container_name: duplicati-notifications
```