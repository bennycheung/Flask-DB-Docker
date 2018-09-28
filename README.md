## Microservices Architecture
This example has been composed from the Microserivices Architecture style.
With this style, we could provide Runway components with a realistic compostability. We recommend to read the Martin Fowler and James Lewis's white paper on Microservice architecture. Their white paper goes much more in-depth for the drivers behind the [Microservice Architecture](http://martinfowler.com/articles/microservices.html)

Starter microservices documentations:
* [Starter API Documentation](starter-api/README.md)

## Docker Orchestration
We need to bring Docker up and running on the host.

Here is the deployment diagram, which is using Docker containers to deploy all services. The following sections provide detail instructions how to create and start Docker images to create the Starter microservices and their dependencies.

![Starter Microservices Deployment](images/Starter_Microservices_Deployment.png)

Assume all the required docker images are built (describe later in the sections), we can use `docker-compose` command to bring up all the containers,

    $ docker-compose -f docker-compose.yml up -d

Conversely, we can shutdown all the containers by,

    $ docker-compose -f docker-compose.yml down


###Persistent Volumes with Docker - Data-only Container Pattern

-- Dockerfile --

    FROM busybox
    VOLUME /var/lib/postgresql/data
    CMD /bin/sh

To create the volume image:

    $ cd busybox
    $ docker build -t db/postgres_datastore .

To start the volume image container:

    $ docker run -i -t --name postgres_data db/postgres_datastore

Since the postgres_data container likely won't ever need to be updated, and if it does we can easily handle moving the data around as needed, we essentially work-around the issues of losing container data and we still have good portability.

We can now create as many postgres_data instances as we can handle and use volumes from as many postgres_data style containers as we want as well (provided unique naming or use of container ID's). This can much more easily be scripted than mounting folders ourselves since we are letting docker do the heavy lifting.

One thing that's really cool is that these data-only containers don't even need to be running, it just needs to exist.

### Create Postgres DB Image
--------------------------
-- Dockerfile --

    FROM postgres:9.3

    RUN apt-get update && apt-get install -y vim-tiny

    EXPOSE 5432

To create the DB image:

    $ cd db
    $ docker build -t db/postgres .

To start the DB image container:

    $ docker run -d \
        -e POSTGRES_USER=docker \
        -e POSTGRES_PASSWORD=docker \
        -e POSTGRES_DB=starter \
        --volumes-from postgres_data \
        --name postgres \
        -p 5432:5432 db/postgres

Try connect to db/postgres container,

    $ psql -h localhost -U docker starter

Try to start another postgres container to access the db,
This is linking the named 'db', which we have started, to alias mydb into the container.
We shall start a interactive shell `-ti` /bin/sh. The container will be automatically
destroyed after running by `--rm` remove container parameter.

    $ docker run --rm -ti --link postgres:mydb db/postgres /bin/sh

    After we entered the container, do the following

    # psql -h mydb -U docker starter
    Password for user docker: <docker> 
    psql (9.3.6)
    Type "help" for help.

    starter=# \dt
                 List of relations
     Schema |       Name       | Type  | Owner  
    --------+------------------+-------+--------
     public | starter_pxcodes  | table | docker
     public | starter_users    | table | docker
    (4 rows)

    We can see the linked `mydb` host's `starter` database.


### Create API starter-api Image
-----------------------
You can read the microservices [Starter API Documentation](starter-api/README.md)

-- Dockerfile --

    FROM python:3.5

    RUN mkdir /app
    WORKDIR /app

    ADD requirements.txt /app/
    RUN pip install -r requirements.txt

    ADD . /app

To create the Starter API image:

    $ cd starter-api
    $ docker build -t starter-api .

To start the Starter API container:

    $ docker run -d -t \
        -v `pwd`/logs:/app/logs \
        --name starter-api \
        --link postgres:postgres \
        -p 5000:5000 starter-api


### Import Medical Procedural Codes into DB
--------------------------
This instance, however, needs to be in the same Docker network as the current running network.
When we started the stack instance, a network called `flask-db-docker_default` was created.
To confirm this, we can run `docker network ls`.

    $ docker network ls

    NETWORK ID          NAME                      DRIVER              SCOPE
    e337657076ec        bridge                    bridge              local
    88cc0cfe1cc7        composer_default          bridge              local
    945ac8820956        flask-db-docker_default   bridge              local
    7749efcaa3dc        host                      host                local
    0c4c4f14a186        none                      null                local

We should see the `postgres` and `starter-api` are part of the `flask-db-docker_default` network,

    $ docker network inspect flask-db-docker_default

    ...
    "Containers": {
        "b43291da217f705ea3d1676fb757b1dafc7c8fdf18f2df32d441e248a6ab8b31": {
            "Name": "postgres",
            "EndpointID": "d01bdf7da8de378b51928a7e7e2a55fab6995865ea5d1c7793e9923c9409f287",
            "MacAddress": "02:42:ac:1d:00:03",
            "IPv4Address": "172.29.0.3/16",
            "IPv6Address": ""
        },
        "e05d5fba146fc4f1c018df41f1cae6bf4fe3d54395572cd73b2c3a3c9bbf859b": {
            "Name": "starter-api",
            "EndpointID": "19e27585ae2005d6310bc6ec8dfbfe8a405400cb4196bfd90206a1fbd9f5700c",
            "MacAddress": "02:42:ac:1d:00:02",
            "IPv4Address": "172.29.0.2/16",
            "IPv6Address": ""
        }
    }

Then we shall start an instance of `starter-api` container to join the `flask-db-docker_default` network,
so that we can access to the same `postgres` database connection.

    $ docker run --rm -ti --network flask-db-docker_default starter-api /bin/sh

After we enter the container, we can execute the initial `starter` database creation
by running the following `starter-api` commands,

    $ python manage.py createdb

We create a new user `admin` with the password `admin` (of course this is not secure)

    $ python manage.py adduser admin admin

After the database has been created, we can exercise the database by inserting
all the medical procedural codes from `data/starter_pxcodes.sql` into the `starter_pxcodes` table

    $ psql -h localhost -U docker starter < data/starter_pxcodes.sql

We can get the medical procedural data from the `starter-api` that we have run.

    $ http --auth admin:admin http://localhost:5000/api/v1.0/pxcodes/

You should see the paged JSON response.

```
HTTP/1.0 200 OK
Content-Length: 15973
Content-Type: application/json
Date: Thu, 27 Sep 2018 22:18:00 GMT
ETag: "678ca404a51794f10b8747ea1eeb4959"
Server: Werkzeug/0.9.6 Python/3.5.6

{
    "items": [
        {
            "procedure": "EXTRACRANIAL PROCEDURES W/O CC/MCC",
            "pxcode": "039",
            "url": "http://localhost:5000/api/v1.0/pxcodes/039"
        },
        {
            "procedure": "DEGENERATIVE NERVOUS SYSTEM DISORDERS W/O MCC",
            "pxcode": "057",
            "url": "http://localhost:5000/api/v1.0/pxcodes/057"
        },
        ... skipped ...
    ],
    "meta": {
        "first": "http://localhost:5000/api/v1.0/pxcodes/?per_page=100&page=1",
        "last": "http://localhost:5000/api/v1.0/pxcodes/?per_page=100&page=1",
        "next": null,
        "page": 1,
        "pages": 1,
        "per_page": 100,
        "prev": null,
        "total": 100
    }
}

```
