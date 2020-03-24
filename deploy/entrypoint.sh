#!/bin/bash
APP=/app
cd $APP
mkdir -p deploy/logs/
touch deploy/logs/supervisord.log
for a in `ls $APP"/"apps`
  do
    if [ -d $APP"/"apps"/"$a ]
    then
      cd $APP"/"apps"/"$a
      mkdir migrations
      cd migrations
      touch __init__.py
    fi
  done
if [ -f $APP"/"deploy"/"celerybeat.pid ]; then
rm -r $APP"/"deploy"/"celerybeat.pid
fi

if [ -f $APP"/"deploy"/"celerybeat-schedule ]; then
rm -r $APP"/"deploy"/"celerybeat-schedule
fi


cd $APP
yes | python manage.py collectstatic
yes | python manage.py rebuild_index
python manage.py makemigrations && python manage.py migrate
exec supervisord -c /app/deploy/supervisord.conf