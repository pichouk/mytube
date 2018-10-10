#!/bin/sh

CONFIG_FILE="/config/settings.py"
# Read environment variables or set default values
FQDN=${FQDN:-localhost}
REFRESH_INTERVAL_MINUTES=${REFRESH_INTERVAL_MINUTES:-60}
RETENTION_INTERVAL_HOURS=${RETENTION_INTERVAL_HOURS:-24}
LANGUAGE_CODE=${LANGUAGE_CODE:-fr-FR}
TIME_ZONE=${TIME_ZONE:-UTC}
PG_DBNAME=${PG_DBNAME:-mytube}
PG_USER=${PG_USER:-mytube}
PG_HOST=${PG_HOST:-db}
PG_PORT=${PG_PORT:-5432}

# Function to generate Django-like secret keys
generate_key() {
  python3 -c 'import random; result = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]); print(result)'
}

# Create configuration file if needed
if [ ! -f $CONFIG_FILE ]
then
  echo "No configuration file "$CONFIG_FILE
  echo "Creating a new one"
  # Copy default configuration file
  cp /code/mytube/settings_example.py $CONFIG_FILE
  # Set some values
  sed -i "s/<<\$FDQN\$>>/$FQDN/g" $CONFIG_FILE
  sed -i "s/<<\$LANGUAGE_CODE\$>>/$LANGUAGE_CODE/g" $CONFIG_FILE
  sed -i "s/<<\$TIME_ZONE\$>>/$TIME_ZONE/g" $CONFIG_FILE

  # Set secret key
  if [ -z "$DJANGO_SECRET_KEY" ]
  then
    sed -i "s/<<\$SECRET_KEY\$>>/$(generate_key)/g" $CONFIG_FILE
  else
    sed -i "s/<<\$SECRET_KEY\$>>/$DJANGO_SECRET_KEY/g" $CONFIG_FILE
  fi

  # Configure retention
  if [ ! -z "$MAX_DAY_RETENTION" ]
  then
    sed -i -E "s/^# retention_time_config #(.*)/\1/g" $CONFIG_FILE
    sed -i "s/<<\$MAX_DAY_RETENTION\$>>/$MAX_DAY_RETENTION/g" $CONFIG_FILE
  fi
  if [ ! -z "$MAX_VIDEO_RETENTION" ]
  then
    sed -i -E "s/^# retention_number_config #(.*)/\1/g" $CONFIG_FILE
    sed -i "s/<<\$MAX_VIDEO_RETENTION\$>>/$MAX_VIDEO_RETENTION/g" $CONFIG_FILE
  fi

  # Configure database
  if [ -z "$PG_PASSWORD" ]
  then
    # SQLite
    sed -i -E "s/^# sqlite_config #(.*)/\1/g" $CONFIG_FILE
    # Create symbolic links to point to SQLite database file
    ln -s /data/database.sqlite3 /code/database.sqlite3
  else
    # PostgreSQL
    sed -i -E "s/^# pg_config #(.*)/\1/g" $CONFIG_FILE
    sed -i "s/<<\$PG_DBNAME\$>>/$PG_DBNAME/g" $CONFIG_FILE
    sed -i "s/<<\$PG_USER\$>>/$PG_USER/g" $CONFIG_FILE
    sed -i "s/<<\$PG_PASSWORD\$>>/$PG_PASSWORD/g" $CONFIG_FILE
    sed -i "s/<<\$PG_HOST\$>>/$PG_HOST/g" $CONFIG_FILE
    sed -i "s/<<\$PG_PORT\$>>/$PG_PORT/g" $CONFIG_FILE

    # Wait for database to be reachable
    echo "Wait until database $PG_HOST:$PG_PORT is ready..."
    until nc -z $PG_HOST $PG_PORT
    do
      sleep 1
    done
  fi
fi

# Create symbolic links to point to configuration file
ln -s $CONFIG_FILE /code/mytube/settings.py

# Check migrations
pipenv run python manage.py showmigrations | grep '\[ \]' > /dev/null
if [ $? -eq 0 ]
then
  pipenv run python manage.py migrate
fi

# Collect statics files
pipenv run python manage.py collectstatic --noinput

# Prepare crontab for refresh task
echo "*/${REFRESH_INTERVAL_MINUTES} * * * * cd /code && pipenv run ./manage.py refresh" > /crontab.conf
# Prepare crontab for purge task
if [ ! -z "$MAX_DAY_RETENTION" ] || [ ! -z "$MAX_VIDEO_RETENTION" ]
then
  echo "0 */${RETENTION_INTERVAL_HOURS} * * * cd /code && pipenv run ./manage.py purge" >> /crontab.conf
fi
# Run cron
crontab  /crontab.conf
crond -f &

# Run Gunicorn server
pipenv run gunicorn -w $((($(nproc --all)*2)+1)) \
  --log-level=info --log-file=- --error-logfile=- --access-logfile=- \
  -b 0.0.0.0:8000 mytube.wsgi
