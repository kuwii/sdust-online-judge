#!/bin/bash

echo "====================================="
echo "   SDUST Online Judge Installation   "
echo "                                     "
echo "                   made by _kawaiiQ  "
echo "====================================="
echo ""

# Variables
MYSQL_PASSWD="big_boss"

LOG_FOLDER="installation_logs"
SOFT_LOG="soft.log"
PG_LOG='pg.log'
MYSQL_LOG='mysql.log'
REDIS_LOG='redis.log'
PYTHON_LOG="python.log"
HUSTOJ_LOG="hustoj.log"

# Initialize logs ---------------------------------------------------------------------------------
echo "Initializing log folder ..."
rm -rf ${LOG_FOLDER}/
mkdir ${LOG_FOLDER}

# Update software packages ------------------------------------------------------------------------
sudo echo deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main > /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
  sudo apt-key add -
echo "Updating software package indices ..."
sudo apt-get update 2>&1 | tee -a ${LOG_FOLDER}/${SOFT_LOG}
echo "Updating software packages ..."
sudo apt-get dist-upgrade -y 2>&1 | tee -a ${LOG_FOLDER}/${SOFT_LOG}
echo "Removing unused software packages ..."
sudo apt-get autoremove -y 2>&1 | tee -a ${LOG_FOLDER}/${SOFT_LOG}

# Install PostgreSQL, Redis and MySQL -------------------------------------------------------------
echo "Installing PostgreSQL, Redis and MySQL ..."
# Install PostgreSQL
sudo apt-get install -y postgresql-9.6 postgresql-contrib-9.6 libpq-dev 2>&1 | tee -a ${LOG_FOLDER}/${PG_LOG}
# Install Redis
sudo apt-get install -y redis-server 2>&1 | tee -a ${LOG_FOLDER}/${REDIS_LOG}
# Install MySQL
echo mysql-server mysql-server/root_password password ${MYSQL_PASSWD} | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password ${MYSQL_PASSWD} | sudo debconf-set-selections
sudo apt-get install -y mysql-server 2>&1 | tee -a ${LOG_FOLDER}/${MYSQL_LOG}

# Configure PostgreSQL and MySQL ------------------------------------------------------------------
echo "Configuring PostgreSQL, Redis and MySQL ..."
# Configure PostgreSQL
sudo mv /etc/postgresql/9.6/main/pg_hba.conf /etc/postgresql/9.6/main/pg_hba.conf.bak
sudo mv /etc/postgresql/9.6/main/postgresql.conf /etc/postgresql/9.6/main/postgresql.conf.bak
sudo cp pg_hba.conf /etc/postgresql/9.6/main/pg_hba.conf
sudo cp postgresql.conf /etc/postgresql/9.6/main/postgresql.conf
sudo chmod 640 /etc/postgresql/9.6/main/pg_hba.conf
sudo chmod 644 /etc/postgresql/9.6/main/postgresql.conf
sudo chown postgres /etc/postgresql/9.6/main/pg_hba.conf
sudo chown postgres /etc/postgresql/9.6/main/postgresql.conf
# Configure Redis
sudo mv /etc/redis/redis.conf /etc/redis/redis.conf.bak
sudo cp redis.conf /etc/redis/redis.conf
sudo chmod 644 /etc/redis/redis.conf
sudo chown root /etc/redis/redis.conf
# Create Database of PostgreSQL
CUR_PATH=$(pwd)
sudo su - postgres -c psql < ${CUR_PATH}/pg.sql 2>&1 | tee -a ${CUR_PATH}/${LOG_FOLDER}/${PG_LOG}
# Create Database of MySQL
sudo mysql -h localhost -uroot -p${MYSQL_PASSWD} < ${CUR_PATH}/mysql.sql 2>&1 | tee -a ${CUR_PATH}/${LOG_FOLDER}/${MYSQL_LOG}

# Start services
echo "Starting services of PostgreSQL, Redis and MySQL ..."
sudo /etc/init.d/postgresql restart 2>&1 | tee -a ${LOG_FOLDER}/${PG_LOG}
sudo service redis-server restart 2>&1 | tee -a ${LOG_FOLDER}/${PG_LOG}
sudo /etc/init.d/mysql restart 2>&1 | tee -a ${LOG_FOLDER}/${MYSQL_LOG}

# Install HUSTOJ judge ----------------------------------------------------------------------------
echo "Installing HUSTOJ judge ..."
#try install tools
sudo apt-get install -y make flex g++ clang libmysql++-dev mono-gmcs subversion
#create user and homedir
sudo  /usr/sbin/useradd -m -u 1536 judge
#compile and install the core
cd hustoj-read-only/core/
sudo sh make.sh
cd ../..
#create work dir set default conf
sudo    mkdir /home/judge
sudo    mkdir /home/judge/etc
sudo    mkdir /home/judge/data
sudo    mkdir /home/judge/log
sudo    mkdir /home/judge/run0
sudo    mkdir /home/judge/run1
sudo    mkdir /home/judge/run2
sudo    mkdir /home/judge/run3
sudo cp java0.policy  judge.conf /home/judge/etc
sudo chown -R judge /home/judge
sudo chgrp -R $APACHEUSER /home/judge/data
sudo chgrp -R root /home/judge/etc /home/judge/run?
sudo chmod 775 /home/judge /home/judge/data /home/judge/etc /home/judge/run?
#boot up judged
sudo cp judged /etc/init.d/judged
sudo chmod +x  /etc/init.d/judged
sudo ln -s /etc/init.d/judged /etc/rc3.d/S93judged
sudo ln -s /etc/init.d/judged /etc/rc2.d/S93judged
sudo /etc/init.d/judged start

# Install Python and related packages -------------------------------------------------------------
echo "Installing Python3 environment ..."
sudo apt-get install python3 python3-pip -y 2>&1 | tee -a ${LOG_FOLDER}/${PYTHON_LOG}
echo "Installing Python packages ..."
sudo -H pip3 install -i https://mirrors.aliyun.com/pypi/simple redis==2.10.5 psycopg2==2.6.2 pymysql==0.7.9 sqlalchemy==1.1.5 django==1.10.5 djangorestframework==3.5.3 django-crispy-forms==1.6.1 drfdocs==0.0.11 drf-nested-routers==0.11.1 django-filter==1.0.1 2>&1 | tee -a ${LOG_FOLDER}/${PYTHON_LOG}
