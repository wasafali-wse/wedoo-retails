# Wedoo 

Wedoo is the Modern, Efficient, Scalable, Customizable and User-friendly Business Management Tool developed by [WAHEEDSONS ENGINEERING](https://waheedsons-engineering.com).
It is designed in Modular structure to and some basic Modules and some special modules can be designed to meet Specific requirements.

## Businesses Can Consider Wedoo

- General Retails Businesses
- Repair Service Providers
- Out Door Service Providers
- Bakeries
- Freelancers
- Online Tutors
- Gyms
- Others

## What You can do with Wedoo In Your Business

- You can Track Sales
- You can Manage Inventory
- You can Manage vendors
- You can Generate labels for Inventory
- You can manage After Sales Services
- You can Generate Reports.
- You have Access Control based Users
 
## Installation & Deployment

Since our Project is basically made with Django Using its power of Default Admin Panel. we need to Deploy the Django project in Windows Machine, but It is recommended to deploy it on a Linux Machine (FEDORA-SERVER or UBUNTU-SERVER). you can prefer Hostings like [Websouls](https://websouls.com/), [Hetzner](https://www.hetzner.com/), [AWS](https://aws.amazon.com/), [Google](https://cloud.google.com/).

We will Setup the Project for Production.
- Use COOLIFY for deployments If you prefer Serverless Experience.
- Use Linux Terminal If you are comfortable with CLI (COMMAND LINE INTERFACE)

We are using the CLI In Fedora-Server.

## wait is over Install is begin

first install fedora-Server. create user to access the machine via SSH.

```bash
C:\User\Desktop> ssh any-user@Server-ip # make sure to use actual user name and server ip 
```
after loggingIn Update the machine.

```bash
sudo dnf -y update
```
then we will Install Postgres database. Initialize database. add Postgres to systemd to start the database server on boot. and allow firewall to use Database. and create Database along User.

```bash
sudo dnf install -y postgresql-server postgresql-contrib # Installs the database 
sudo postgresql-setup --initdb # Initialize the DB.
sudo systemctl start postgresql # Start the database.
sudo systemctl enable postgresql # Enable the Service to start on boot.
sudo firewall-cmd --add-service=postgresql --permanent # Allow the firewall.
sudo firewall-cmd --reload # reload the firewall. to apply changes.
CREATE DATABASE myprojectdb; # remove witrh actual name 
CREATE USER myprojectuser WITH PASSWORD 'your_password'; # make sure to use strong password
GRANT ALL PRIVILEGES ON DATABASE myprojectdb TO myprojectuser; # make sure to use actual details.
\q
```
Once the Database is Setup correctly. move to next Step.
we will create a Dir to Keep our project Organized.

```bash
sudo mkdir -p /var/www # this will create dir.
cd /var/www # navigate to the dir.
# change the ownership to user optional
sudo chown -R yourusername:yourusername /var/www
sudo chmod -R 755 /var/www
```
Now we will clone the Project

```bash
sudo git clone https://github.com/wasafali-wse/wedoo.git # clones the project 
cd wedoo # we are in root dir
python3 -m venv venv # its time to create virtual environment.
source venv/bin/activate # activate environment
pip install -r requirements.txt # this installs the dependencies in the environment.
```
now we need to set some production settings to our project. so in settings.py 

```wedoo/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myprojectdb', # the actual one
        'USER': 'myprojectuser', # the actual one
        'PASSWORD': 'your_password', # the actual one
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Now Migrate database.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser 
```
Now Collect statics.

```bash
python manage.py collectstatic
```
Now we need to Configure a Reverse Proxy (Nginx)

so create a file /etc/nginx/sites-available/wedoo

```bash
sudo nano /etc/nginx/conf.d/wedoo.conf.
```
and put this in conf file 

```wedoo.conf
server {
	    listen 192.168.xxx.xxx:80;  # or just 'listen 80;'
		        server_name _;  # or specify your domain or IP

			    # Serve static files
			    location /static/ {
				            alias /var/www/wedoo/staticfiles/;  # match STATIC_ROOT
						        }

	        # Serve media files
	        location /media/ {
			        alias /var/www/wedoo/media/;  # match MEDIA_ROOT
					    }

		    # Proxy pass to Gunicorn
		    location / {
			            proxy_pass http://127.0.0.1:8000;  # Gunicorn is running here
					            proxy_set_header Host $host;
				            proxy_set_header X-Real-IP $remote_addr;
					            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
						            proxy_set_header X-Forwarded-Proto $scheme;
							        }
}

```
always a good idea to check syntex

```bash
sudo nginx -t
```

then reload the services

```bash
sudo systemctl reload nginx
```
Now its time to create a gunicorn service to start the project on boot.

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add thes to file.

```gunicorn.service
[Unit]
Description=Gunicorn instance to serve Application
After=network.target

[Service]
User=wasaf
Group=nginx
WorkingDirectory=/var/www/wedoo
ExecStart=/bin/bash -c 'source /var/www/wedoo/venv/bin/activate && exec /var/www/wedoo/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wedoo.wsgi:application'
Restart=always

[Install]
WantedBy=multi-user.target
```
By now we must have our project running successfully.