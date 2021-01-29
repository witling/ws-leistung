# ws-leistung

Start

```
docker-compose up --build
```

Service will be available at `localhost:4000`.

## Docs

- [Python 3](https://www.tutorialspoint.com/python/index.htm)
- [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [jinja (Template Sprache)](https://jinja.palletsprojects.com/en/2.11.x/)
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