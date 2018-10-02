# Mytube

This project aims to provide a simple Web interface to manage Youtube channel subscriptions without a Youtube/Google account. Mytube runs using Python framework `Django` and `pipenv` to manage dependencies.

## Build

You can simply build Mytube with Docker using `docker build -t mytube .`

## Configuration

You need to provide several environment variables to your Mytube container to configure the application.
- `FQDN` : FQDN of your Mytube instance (eg. `mytube.mydomain.fr`)

## Run

To run your image in production, I recommend using Docker Compose to manage containers needed to run Mytube : Mytube application, a webserver for static files, maybe a database, etc.

You can create a `docker-compose.yml` file (example can be found at the end of this *README*) to setup your containers, configure some environment variables (see *Configuration* part above), mount volumes, etc.

### Volumes

To ensure data persistence, you will need to provide some volumes to your container :
- one for `/statics` folder that will contains all static files of Django. This volume **MUST** be shared with another container that is able to serve those static files.
- one for `/config` folder, that will only contains the `settings.py` file for Django. If you don't mount one, your configuration will be reset at each container startup. In practice it will only reset your Django secret key.
- one for `/data` folder **only if you use SQLite** (default option)

### Expose

I recommend to expose your Mytube instance with a reverse proxy (I use Traefik). The reverse proxy should be configured to forward all requests to the Mytube container (port `8000`) except for everything under `/static` path, that should be serve by another web server (Apache, Nginx, etc.)

# Examples

I use Traefik to expose my containers.

```yml
version: '3'
services:
  mytube:
    image: mytube
    container_name: mytube
    environment:
      - FQDN=mytube.domain.fr
    volumes:
      - /path/to/volumes/mytube/config:/config
      - /path/to/volumes/mytube/static:/statics
      - /path/to/volumes/mytube/data:/data
    labels:
        - "traefik.frontend.rule=Host:mytube.domain.fr"
        - "traefik.port=8000"
        - "traefik.enable=true"
    restart: always

  mytube-static:
    image: nginx:stable-alpine
    container_name: mytube-static
    volumes:
      - /path/to/volumes/mytube/static:/usr/share/nginx/html/static:ro
    labels:
      - "traefik.frontend.rule=Host:mytube.domain.fr;PathPrefix:/static"
      - "traefik.port=80"
      - "traefik.enable=true"
    restart: always
```

# TODO on Mytube
- Use cronjob to refresh
- Add support for PostgreSQL
- Create a function that purge all videos older than a date. Use cron to run this function (at a specific interval).
- Add support for users.
