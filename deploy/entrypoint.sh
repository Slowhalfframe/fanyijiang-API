#!/bin/bash
APP=/app
cd $APP
touch deploy/logs/supervisord.log
exec supervisord -c /app/deploy/supervisord.conf