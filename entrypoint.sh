#!/bin/sh

CONFIG_FILE="/config/settings.py"
# Read environment variables or set default values
FQDN=${FQDN:-localhost}
REFRESH_INTERVAL_MINUTES=${REFRESH_INTERVAL_MINUTES:-60}
LANGUAGE_CODE=${LANGUAGE_CODE:-fr-FR}
TIME_ZONE=${TIME_ZONE:-UTC}

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

fi

# Create symbolic links to point to configuration file
ln -s $CONFIG_FILE /code/mytube/settings.py

# Create symbolic links to point to SQLite database file
ln -s /data/database.sqlite3 /code/database.sqlite3

# Check migrations
pipenv run python manage.py showmigrations | grep '\[ \]' > /dev/null
if [ $? -eq 0 ]
then
  pipenv run python manage.py migrate
fi

# Collect statics files
pipenv run python manage.py collectstatic --noinput

# Prepare crontab for refresh task
echo "*/${REFRESH_INTERVAL_MINUTES} * * * * curl http://localhost:8000/refresh/" > /crontab.conf
crontab  /crontab.conf
crond

# Run Django server
pipenv run python manage.py runserver 0.0.0.0:8000
