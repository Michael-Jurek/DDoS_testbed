# DDoS testbed
Web application for testing selected DDoS attacks. The botnet and the victim server is generated using Docker containers, the impact of the attacks is then visualized using Grafana. The following description is for the Linux operating system, commands may vary slightly from distribution to distribution.
## Requirements

- Python3 
- Venv
- Docker - you have to have rights to use docker without sudo <!--  https://docs.docker.com/engine/install/linux-postinstall -->
```
sudo groupadd docker            # Create docker group - some linux distributions already have
sudo usermod -aG docker $USER   # Add your user to the docker group 
newgrp docker                   # Activate the group changes
```
- Docker Compose


## Installation
- Get this repository
- Get to /web_app/, create virtual environment and activate it
```
cd DDoS_testbed/web_app/
python3 -m venv ./venv
. venv/bin/activate
```
- Install necessary packages
```
python3 -m pip install -r requirements.txt
```
- Start the app
```
flask run  # If you want the app to be accessible from other devices on the network -> flask run --host=0.0.0.0
```
- App is running on http://localhost:5000 

## Some notes
- It can take a long time to run the application for the first time, the Docker has to pull the necessary images. In the case of the first botnet generation or changing Apache version, the same applies, but once everything is downloaded, there should no longer be a higher delay.

- Default role in Grafana is Viewer, if you want to enable editing log in with username **admin** and password **1234**.
