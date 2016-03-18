#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pony import orm
from pony.orm import db_session

from flask_script import Manager
from mini_fiction import application

manager = Manager(application.create_app())


@manager.command
def shell():
    import code
    import mini_fiction
    from mini_fiction import models
    with db_session:
        code.interact(local={'mini_fiction': mini_fiction, 'app': manager.app, 'm': models})


@manager.command
def seed():
    from mini_fiction import fixtures
    orm.sql_debug(False)
    with db_session:
        fixtures.seed()


@manager.command
def initsphinx():
    from mini_fiction.management.commands.initsphinx import initsphinx as cmd
    orm.sql_debug(False)
    with db_session:
        cmd()


@manager.command
def collectstatic():
    from mini_fiction.management.commands.collectstatic import collectstatic as cmd
    orm.sql_debug(False)
    with db_session:
        cmd()


@manager.command
def createsuperuser():
    from mini_fiction.management.commands.createsuperuser import createsuperuser as cmd
    orm.sql_debug(False)
    with db_session:
        cmd()


@manager.command
def checkstorycomments():
    from mini_fiction.management.commands.checkcomments import checkstorycomments as cmd
    orm.sql_debug(False)
    with db_session:
        cmd()


@manager.command
def checknoticecomments():
    from mini_fiction.management.commands.checkcomments import checknoticecomments as cmd
    orm.sql_debug(False)
    with db_session:
        cmd()


@manager.command
def dumpdb(dirpath, models_list):
    from mini_fiction.management.commands.dumploaddb import dumpdb as cmd
    orm.sql_debug(False)
    with db_session:
        cmd(dirpath, [x.strip().lower() for x in models_list.split(',')])


@manager.command
def loaddb(pathlist):
    from mini_fiction.management.commands.dumploaddb import loaddb as cmd
    orm.sql_debug(False)
    with db_session:
        cmd([x.strip() for x in pathlist.split(',')])


@manager.option('-h', '--host', dest='host', help='Server host (default 127.0.0.1)')
@manager.option('-p', '--port', dest='port', help='Server port (default 5000)', type=int)
@manager.option('-t', '--threaded', dest='threaded', help='Threaded mode', action='store_true')
def runserver(host, port=None, threaded=False):
    manager.app.run(
        host=host,
        port=port,
        threaded=threaded
    )


def run():
    manager.run()

if __name__ == "__main__":
    run()
