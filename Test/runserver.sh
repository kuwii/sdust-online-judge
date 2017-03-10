#!/usr/bin/env bash
echo "========================================"
echo "     SDUST Online Judge Test Runner     "
echo "========================================"

echo "WARNING: This is used ONLY FOR TEST!"

echo "Starting Django service ..."
cd ../Server/sdustoj_server/
# python3 manage.py makemigrations
# python3 manage.py migrate
# nohup python3 manage.py runserver >> server.log 2>&1 &
cd ../../

echo "Starting HUSTOJ Adapter ..."
cd Judge/adapter-hustoj/
cd Client/
nohup sudo python3 app.py >> client_writer.log 2>&1 &
cd ../
cd Manager/
sudo sh app.sh
cd ../..

echo "Service started"