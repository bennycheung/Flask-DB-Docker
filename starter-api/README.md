# Starter API - RESTful Web Services with Flask
================================================
The API in this example implements the data microservice for Starter API systems and demonstrates RESTful principles,
CRUD operations, error handling, user authentication, pagination, rate limiting and HTTP caching controls.

## Credits
-------
Thanks to Miguel Grinberg's Pycon 2014 Talk on Flask RESTful Web Service to make this Runway example possible.
* Video at https://www.youtube.com/watch?v=px_vg9Far1Y


## Requirements
------------

To install and run this application you need:

> see installation instruction below

- Anaconda Python 3.5
- Anaconda virtual environment
- git (only to clone this repository, https://locate_at_somewhere)

## Installation
------------

### Anaconda Python
Ref: <https://www.continuum.io/downloads>

Anaconda is an easy-to-install free package manager,
environment manager, Python distribution, and collection of over 720 open source packages offering free community support.

You can install either Anaconda Python 2.7 or Anaconda Python 3.5 on any platform.
Later, we would create a virtual environment to isolate our application specific tools installation.
We shall refer to your Anaconda installation location as {path_to_anaconda_location} later.

### Setup Environment
The commands below install the application and its dependencies:

```
git clone https://locate_at_somewhere
cd starter-api
```

By experience, hacking on a new tools suite are usually messy and full of conflicts.
Using an isolated Python virtual environment will protect you from headaches and disaster of installations.
In bash shell, enter the following where `starter` (or your choice of name) is the name of the virtual environment,
and `python=3.5` is the Python version you wish to use.

```
conda create -n starter python=3.5 anaconda
```

Press y to proceed. This will install the Python version and all the associated anaconda packaged libraries at `{path_to_anaconda_location}/envs/starter`

Once the `starter` virtual environment has been installed, activate the virtualenv by

```
source activate starter
```

Then, install all the modules specified in `requirements.txt`

```
pip install -r requirements.txt
```

> Note for Microsoft Windows users: replace the virtual environment activation command above with `venv\Scripts\activate`.

The core dependencies are Flask, Flask-HTTPAuth, Flask-SQLAlchemy, Flask-Script and redis (only used for the rate limiting feature).
For unit tests nose and coverage are used. The httpie command line HTTP client is also installed as a convenience.

## Create Database
---------------

The API is default to operate on PostgreSQL database. We need to create an empty `starter` database with the following commands:

(1) Create DB owner:

```
su - postgres (if not, use sudo -u postgres)
```

> or if your username is a superuser in PostgreSQL account, you can skip the `su` to root)

```
createuser -s -P admin
```

> suggested using password for development: admin, where all examples are shown later)

```
createdb --owner=admin starter
```

(2) Synchronized API project schemas with DB

```
python manage.py createdb
```

> beware the database tables are rebuilt, all previous data are dropped.

Use `psql` to view the created database `starter`.

```
psql starter --username=admin --password

Password for user admin:

psql (10.2)
Type "help" for help.

starter=# \l
                                    List of databases
      Name      |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
----------------+----------+----------+-------------+-------------+-----------------------
...
 starter        | admin    | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
...
(7 rows)
```

The `starter` database are composed from,
* `starter_users` is used for maintaining valid API users and their credentials.
* `starter_pxcodes` (just for initial tutorial database table, which is the medical procedure code and description)

```
starter=# \d
                  List of relations
 Schema |           Name           |   Type   | Owner
--------+--------------------------+----------+-------
 public | starter_pxcodes          | table    | admin
 public | starter_pxcodes_id_seq   | sequence | admin
 public | starter_users            | table    | admin
 public | starter_users_id_seq     | sequence | admin
(4 rows)
```

## User Registration
-----------------

The API can only be accessed by authenticated users. New users can be registered with the application from the command line:

```
python manage.py adduser <username>

Password: <password>
Confirm: <password>
User <username> was registered successfully.
```

For example, `<username>` admin and `<password>` admin are used in this document examples.

The system supports multiple users, so the above command can be run as many times as needed with different usernames.
Users are stored in the application's database, which by default uses the PostgreSQL engine.
An empty database is created in the current folder if a previous database file is not found.


## Running Server
--------------
NOTE: Running the server for the first time, you need to create database and user.
(see later sections on Create Database and User Registration)

To run a development server:

```
python manage.py runserver
```

You should see,
```
Running on http://127.0.0.1:5000/
Restarting with reloader
```

You can start the server with different port with `-p 8000`, for example:


## Unit Tests
----------

To ensure that your installation was successful you can run the unit tests:

```
python manage.py test

Name              Stmts   Miss Branch BrMiss  Cover   Missing
-------------------------------------------------------------
api                   0      0      0      0   100%
api.auth             13      6      2      2    47%   11-18, 23
api.decorators       86     67     28     27    18%   24-38, 43-62, 69-94, 103-111, 115, 122-138
api.errors           31     21      0      0    32%   9-11, 15-18, 22-25, 29-32, 36-39, 43-45, 49-52
api.helpers          22     17     11     11    15%   10-30, 34-37
api.models           50     22      0      0    56%   29, 32, 39-49, 61, 65, 68, 71-72, 76-81
api.rate_limit       38     23      6      6    34%   12-13, 16, 19-22, 25, 28, 36-49, 53, 57
api.v1_0             16      6      2      2    56%   16, 21, 26, 38-40
api.v1_0.pxcode      18      6      0      0    67%   19, 26, 32-35
-------------------------------------------------------------
TOTAL               274    168     49     48    33%
----------------------------------------------------------------------
Ran 0 tests in 0.153s

OK
```

The report printed below the tests is a summary of the test coverage. A more detailed report is written to a `cover` folder. To view it, open `cover/index.html` with your web browser.



## API Documentation
-----------------

The API supported by this application contains three top-level resources:

- `/api/v1.0/pxcodes/`: The collection of procedures.

All other resource URLs are to be discovered from the responses returned from the above three.


### Resource Collections

All resource collections have the following structure:

    {
        "items": [
            [ITEM 1 JSON],
            [ITEM 2 JSON],
            ...
        ],
        "meta": {
            "page": [current_page],
            "pages": [total_page_count],
            "per_page": [items_per_page],
            "total": [total item count],
            "prev": [link to previous page],
            "next": [link to next page],
            "first": [link to first page],
            "last": [link to last page]
        }
    }

The `items` key contains an array with the items of the requested resources. Note that results are paginated, so not all the resource in the collection might be returned. Clients should use the navigation links in the `meta` portion to obtain more resources.

### Procedure Resource

A procedure resource has the following structure:

    {
        "url": [procedure self URL],
        "pxcode": [procedure code],
        "procedure": [procedure description]
    }

When creating or updating a procedure resource both the `pxcode` and `procedure` fields need to be provided. The following example creates a procedure resource by sending a `POST` request to the top-level pxcodes URL. The `httpie` command line client is used to send this request.

The parameter `--auth <username>:<password>` can be used to send Authorization header. If plain `<password>` is not desirable, user can just put `--auth <username>` and `httpie` will prompt for `<password>` such that the secret is not visible. We shall discuss token-based authorization in later section.

    (starter) $ http --auth admin:admin POST http://localhost:5000/api/v1.0/pxcodes/ \
        pxcode="039" \
        procedure="EXTRACRANIAL PROCEDURES W/O CC/MCC"

    HTTP/1.0 201 CREATED
    Content-Length: 2
    Content-Type: application/json
    Date: Mon, 16 Mar 2015 14:26:05 GMT
    Location: http://localhost:5000/api/v1.0/pxcodes/001
    Server: Werkzeug/0.9.4 Python/2.7.6

    {}

Only the `pxcode` field needs to be provided when creating or modifying a procedure resource. Note the `Location` header included in the response, which contains the URL of the newly created resource. This URL can now be used to get specific information about this resource:

    (starter) $ http --auth admin:admin GET http://localhost:5000/api/v1.0/pxcodes/039

    HTTP/1.0 200 OK
    Content-Length: 131
    Content-Type: application/json
    Date: Mon, 23 Mar 2015 03:06:15 GMT
    ETag: "7b5c8a0bc9ab75a1d441ee15511f7313"
    Server: Werkzeug/0.9.6 Python/2.7.9

    {
        "procedure": "EXTRACRANIAL PROCEDURES W/O CC/MCC", 
        "pxcode": "039", 
        "url": "http://localhost:5000/api/v1.0/pxcodes/039"
    }

The procedure resource supports `GET`, `POST`, `PUT` and `DELETE` methods.


## Using Token Authentication
--------------------------

The default configuration uses username and password for request authentication. To switch to token based authentication the configuration stored in `config.py` must be edited. In particular, the line that begins with `USE_TOKEN_AUTH` must be changed to:

    USE_TOKEN_AUTH = True 

After this change restart the application for the change to take effect.

With this change authenticating using username and password will not work anymore. Instead an authentication token must be requested:

    (starter) $ http --auth <username> GET http://localhost:5000/auth/request-token
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 200 OK
    Cache-Control: no-cache, no-store, max-age=0
    Content-Length: 139
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:18:55 GMT
    Server: Werkzeug/0.9.4 Python/2.7
    
    {
        "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTM5NjU3NzkzNSwiaWF0IjoxMzk2NTc0MzM1fQ.eyJpZCI6MX0.8XFUzlGz5XPGJp0weoOXy6avwr7OS1ojMbJYpBvw42I"
    }

The returned token must be sent as authentication for all requests into the API:

    (starter) $ http --auth eyJhbGciOiJIUzI1NiIsImV4cCI6MTM5NjU3NzkzNSwiaWF0IjoxMzk2NTc0MzM1fQ.eyJpZCI6MX0.8XFUzlGz5XPGJp0weoOXy6avwr7OS1ojMbJYpBvw42I: \
        GET http://localhost:5000/api/v1.0/pxcodes/

    HTTP/1.0 200 OK
    Content-Length: 345
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:21:52 GMT
    ETag: "b6ce14e7c7496c7d3b22fff0f0fba666"
    Server: Werkzeug/0.9.4 Python/2.7
    
    {
        "items": [
            "procedure": "EXTRACRANIAL PROCEDURES W/O CC/MCC", 
            "pxcode": "039", 
            "url": "http://localhost:5000/api/v1.0/pxcodes/039"
        ],
        "meta": {
            "page": 1,
            "pages": 1,
            "per_page": 100,
            "total": 1,
            "prev": null,
            "next": null,
            "first": "http://localhost:5000/api/v1.0/pxcodes/?per_page=100&page=1",
            "last": "http://localhost:5000/api/v1.0/pxcodes/?per_page=100&page=1"
        }
    }

Note the colon character following the token, this is to prevent `httpie` from asking for a password, since token authentication does not require one.

## HTTP Caching
------------

The different API endpoints are configured to respond using the appropriate caching directives. The `GET` requests return an `ETag` header that HTTP caches can use with the `If-Match` and `If-None-Match` headers.

The `GET` request that returns the authentication token is not supposed to be cached, so the response includes a `Cache-Control` directive that disables caching.

## Rate Limiting
-------------

This API supports rate limiting as an optional feature. To use rate limiting the application must have access to a Redis server running on the same host and listening on the default port.

To enable rate limiting change the following line in `config.py`:

    USE_RATE_LIMITS = True

The default configuration limits clients to 5 API calls per 15 second interval. When a client goes over the limit a response with the 429 status code is returned immediately, without carrying out the request. The limit resets as soon as the current 15 second period ends.

When rate limiting is enabled all responses return three additional headers:

    X-RateLimit-Limit: [period in seconds]
    X-RateLimit-Remaining: [remaining calls in this period]
    X-RateLimit-Reset: [time when the limits reset, in UTC epoch seconds]

