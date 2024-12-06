Overview
--------

This is the GitHub repo for the blog post: https://www.letsql.com/posts/xgboost-end-to-end/

Installation
------------

### Setting up a development environment

This assumes that you have Python installed.

#### Using pip and venv

```bash
# fetch this repo
git clone git@github.com:letsql/blogpost-sqlglot-demo.git
# enter the directory of the repo
cd blogpost-sqlglot-demo
# prepare development environment
python3 -m venv venv
# activate the venv
source venv/bin/activate
# update pip itself if necessary
python -m pip install -U pip
# install dependencies 
python -m pip install -r requirements-dev.txt
```

#### Using poetry

Install poetry, following these [instructions](https://python-poetry.org/docs/#installing-with-pipx)

```bash
# fetch this repo
git clone git@github.com:letsql/blogpost-sqlglot-demo.git
# enter the directory of the repo
cd blogpost-sqlglot-demo
# prepare development environment 
poetry shell
# install dependencies 
poetry install --sync
```

Execution
---------

For executing the project as is, you will need to have docker compose (see [here](https://docs.docker.com/compose/install/linux/)).
First spin the containers: 

```bash
docker compose --build --wait
```

and then run:

```bash
python workflow.py
```


