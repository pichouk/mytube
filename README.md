# Mytube

This project aims to provide a simple Web interface to manage Youtube channel subscriptions without a Youtube/Google account. Mytube runs using Python framework `Django` and `pipenv` to manage dependencies.

## Build

You can simply build Mytube with Docker using `docker build -t mytube .`

## Configuration

You need to provide several environment variables to your Mytube container to configure the application.
- `FQDN` : FQDN of your Mytube instance (eg. `mytube.mydomain.fr`)

Some other optionnal variables :
- `REFRESH_INTERVAL_MINUTES` : How often your Mytube instance should collect new videos (default is `60`)
- `LANGUAGE_CODE` : Language code for your instance (default is `fr-FR` :p )
- `TIME_ZONE` : Your timezone (defaut is `UTC`)
- `DJANGO_SECRET_KEY` : If you d'ont want to loose your secret key everytime you restart your container, you can give it one. Not mandatory.

## Run

To run your image in production, I recommend using Docker Compose to manage containers needed to run Mytube : Mytube application, a webserver for static files, maybe a database, etc.

You can create a `docker-compose.yml` file (example can be found at the end of this *README*) to setup your containers, configure some environment variables (see *Configuration* part above), mount volumes, etc.

### Volumes

To ensure data persistence, you will need to provide some volumes to your container :
- one for `/statics` folder that will contains all static files of Django. This volume **MUST** be shared with another container that is able to serve those static files.
- one for `/data` folder **only if you use SQLite** (default option)

### PostgreSQL database

By default Mytube use a SQLite database (stored under `/data`), but you can change to use a PostgreSQL database. If you provide a `PG_PASSWORD` environment variables it will try to connect to a PostgreSQL database (it was tested with PostgreSQL 10.5), but you can provide some other variables :
- `PG_DBNAME` : Name of the database to connect (default is `mytube`)
- `PG_USER` : Username to connect to database (default is `mytube`)
- `PG_PASSWORD` : Password to connect to database
- `PG_HOST` : Host address of the PostgreSQL instance (default is `db`)
- `PG_PORT` : Port of PostgreSQL instance (default is `5432`)

### Expose

I recommend to expose your Mytube instance with a reverse proxy (I use Traefik). The reverse proxy should be configured to forward all requests to the Mytube container (port `8000`) except for everything under `/static` path, that should be serve by another web server (Apache, Nginx, etc.)

# Examples

I use Traefik to expose my containers.

With SQLite
```yml
version: '3'
services:
  mytube:
    image: mytube
    container_name: mytube
    environment:
      - FQDN=mytube.domain.fr
    volumes:
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

With PostgreSQL
```yml
version: '3'
services:
  mytube:
    image: mytube
    container_name: mytube
    links:
      - mytube-db:db
    environment:
      - FQDN=mytube.domain.fr
      - PG_PASSWORD=thisisaweakpassword
    volumes:
      - /path/to/volumes/mytube/static:/statics
    labels:
        - "traefik.frontend.rule=Host:localhost"
        - "traefik.port=8000"
        - "traefik.enable=true"
    restart: always

  mytube-db:
    image: postgres:10.5-alpine
    container_name: mytube-db
    volumes:
      - /path/to/volumes/mytube/pg_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=mytube
      - POSTGRES_PASSWORD=thisisaweakpassword
      - POSTGRES_DB=mytube
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
- Create a function that purge all videos older than a date. Use cron to run this function (at a specific interval).
- Add support for users (then `refresh` endpoint will need an ADMIN_KEY)
