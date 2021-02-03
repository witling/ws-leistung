# ws-leistung

Start

``` bash
docker-compose up --scale app=2 --build
```

Service will be available at `localhost:4000`.

## Initial setup

If you are updating the `postgresql` initialization script, make sure to work on a clean volume as the database will not be initialized for non-empty data directories.

``` bash
# make sure the docker-compose system is not running
# delete all unused containers
docker system prune
# delete all unused volumes
docker volume prune
```

## Docs

- [Python 3](https://www.tutorialspoint.com/python/index.htm)
- [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [jinja (Template Sprache)](https://jinja.palletsprojects.com/en/2.11.x/)
- [postgresql](https://www.tutorialspoint.com/postgresql/index.htm)
- [git](https://www.atlassian.com/de/git/tutorials/learn-git-with-bitbucket-cloud)
- [graphical git interface](https://www.sourcetreeapp.com/)

### Git Grundkurs

``` bash
# clone repository to local machine
git clone https://github.com/lausek/ws-leistung; cd ws-leistung

# check status of changes
git status

# create a new project version for the user
git checkout -b <your_username>

# ... modify some files
git add modified-file
git commit -m "changed behavior of database interaction"

# initial git push if branch was just created
git push -u origin <your_username>
# ... or this if branch was already pushed
git push

# change to main project version
git checkout master
git pull
```
