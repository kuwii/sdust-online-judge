DROP DATABASE sdustoj;

CREATE USER korosensei WITH PASSWORD 'big_boss';

CREATE DATABASE sdustoj
    WITH 
    OWNER = korosensei
    ENCODING = 'UTF8';

GRANT ALL PRIVILEGES ON DATABASE sdustoj TO korosensei;

