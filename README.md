# Feature Point Match Serving
It is further developed based on the Opencv ORB detector. It gives the ability to match in the cloud.

# How to install?
- Execute command to install Dependent package. `install -r Sources/requirements.txt`
- Run `python http_server` and `python tcp_server`


# http_server and tcp_server?
- Http Serverr is a API to add new image
- Tcp Server is a predict and matching server

# Add new image by RestFul API
**Post:**
```
//form-data:
image_url:https://xxxx.com/Image.jpg
metadata:Image or json 

```
