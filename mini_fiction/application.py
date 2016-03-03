#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=unused-variable

import os
import importlib
import logging
from logging.handlers import SMTPHandler

from celery import Celery
from werkzeug.contrib import cache
from flask import Flask, current_app, request, g
import flask_babel
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect

from mini_fiction import models  # pylint: disable=unused-import
from mini_fiction import database, tasks
from mini_fiction.bl import init_bl
from mini_fiction.utils.misc import sitename


__all__ = ['create_app']


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ.get('MINIFICTION_SETTINGS', 'mini_fiction.settings.Development'))
    app.static_folder = app.config['STATIC_ROOT']
    init_bl()

    configure_i18n(app)
    configure_cache(app)
    configure_forms(app)
    configure_users(app)
    configure_error_handlers(app)
    configure_views(app)
    configure_ajax_views(app)
    configure_errorpages(app)
    configure_templatetags(app)
    if not app.config['SPHINX_DISABLED']:
        configure_search(app)
    configure_celery(app)
    configure_misc(app)
    configure_development(app)

    app.context_processor(templates_context)

    init_plugins(app)
    database.configure_for_app(app)

    return app


def configure_i18n(app):
    babel = flask_babel.Babel(app)

    @babel.localeselector
    def get_locale():
        locales = app.config['LOCALES'].keys()
        locale = request.cookies.get('locale')
        if locale in locales:
            return locale
        return request.accept_languages.best_match(locales)

    @app.before_request
    def before_request():
        g.locale = flask_babel.get_locale()


def configure_cache(app):
    if app.config.get('MEMCACHE_SERVERS'):
        app.cache = cache.MemcachedCache(app.config['MEMCACHE_SERVERS'], key_prefix=app.config.get('CACHE_PREFIX', ''))
    else:
        app.cache = cache.NullCache()


def configure_forms(app):
    app.csrf = CsrfProtect(app)


def configure_users(app):
    app.login_manager = LoginManager(app)
    app.login_manager.login_view = 'auth.login'
    app.login_manager.anonymous_user = models.AnonymousUser

    @app.login_manager.user_loader
    def load_user(user_id):
        return models.Author.get(id=int(user_id), is_active=1)


def templates_context():
    context = {}
    context.update(current_app.templatetags)
    context.update({
        'SITE_NAME': sitename(),
    })
    return context


def configure_error_handlers(app):
    if app.config['ADMINS'] and app.config['ERROR_EMAIL_HANDLER_PARAMS']:
        params = dict(app.config['ERROR_EMAIL_HANDLER_PARAMS'])
        params['toaddrs'] = app.config['ADMINS']
        params['fromaddr'] = app.config['ERROR_EMAIL_FROM']
        params['subject'] = app.config['ERROR_EMAIL_SUBJECT']
        handler = SMTPHandler(**params)
        handler.setLevel(logging.ERROR)
        app.logger.addHandler(handler)


def configure_views(app):
    from mini_fiction.views import index, auth, story, chapter, search, author, stream, object_lists, comment, feeds, staticpages
    app.register_blueprint(index.bp)
    app.register_blueprint(auth.bp, url_prefix='/accounts')
    app.register_blueprint(story.bp, url_prefix='/story')
    app.register_blueprint(chapter.bp)  # /story/%d/chapter/* and /chapter/*
    app.register_blueprint(search.bp, url_prefix='/search')
    app.csrf.exempt(search.bp)
    app.register_blueprint(author.bp, url_prefix='/accounts')
    app.register_blueprint(stream.bp, url_prefix='/stream')
    app.register_blueprint(object_lists.bp)
    app.register_blueprint(comment.bp)
    app.register_blueprint(feeds.bp, url_prefix='/feeds')
    app.register_blueprint(staticpages.bp, url_prefix='/page')


def configure_ajax_views(app):
    from mini_fiction.ajax.views import story, chapter, comment
    app.register_blueprint(story.bp, url_prefix='/ajax/story')
    app.register_blueprint(chapter.bp, url_prefix='/ajax')
    app.register_blueprint(comment.bp, url_prefix='/ajax')


def configure_errorpages(app):
    from flask import render_template
    from pony.orm import db_session

    def _page403(e):
        return render_template('403.html'), 403

    def _page404(e):
        return render_template('404.html'), 404

    def _page500(e):
        return render_template('500.html'), 404

    app.errorhandler(403)(db_session(_page403))
    app.errorhandler(404)(db_session(_page404))
    app.errorhandler(500)(db_session(_page500))


def configure_templatetags(app):
    from mini_fiction.templatetags import random_stories, submitted_stories_count
    from mini_fiction.templatetags import story_comments_delta, html_block, hook
    from mini_fiction.templatetags import registry
    app.templatetags = dict(registry.tags)


def configure_search(app):
    from mini_fiction.apis import amsphinxql
    app.sphinx = amsphinxql.SphinxPool(app.config['SPHINX_CONFIG']['connection_params'])


def configure_celery(app):
    app.celery = Celery('mini_fiction', broker=app.config['CELERY_BROKER_URL'])
    app.celery.conf.update(app.config)

    TaskBase = app.celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    app.celery.Task = ContextTask

    tasks.apply_for_app(app)


def configure_misc(app):
    @app.after_request
    def call_callbacks(response):
        for f, args, kwargs in getattr(g, 'after_request_callbacks', ()):
            f(*args, **kwargs)
        return response


def configure_development(app):
    if app.config.get('DEBUG_TB_ENABLED'):
        import time
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

        if (
            'mini_fiction.utils.debugtoolbar.PonyDebugPanel' in app.config.get('DEBUG_TB_PANELS', ()) and
            (app.debug or app.config.get('PONYORM_RECORD_QUERIES'))
        ):
            from mini_fiction.utils import debugtoolbar as ponydbg
            from flask_debugtoolbar import module

            old_exec_sql = database.db._exec_sql

            def my_exec_sql(sql, arguments=None, *args, **kwargs):
                t = time.time()
                result = old_exec_sql(sql, arguments, *args, **kwargs)
                t = time.time() - t
                ponydbg.record_query({
                    'statement': sql,
                    'parameters': arguments or (),
                    'duration': t,
                })
                return result
            database.db._exec_sql = my_exec_sql

            app.before_request(ponydbg.clear_queries)
            app.csrf.exempt(module)


def init_plugins(app):
    app.hooks = {}
    with app.app_context():
        for plugin_module in app.config['PLUGINS']:
            if ':' in plugin_module:
                plugin_module, func_name = plugin_module.split(':', 1)
            else:
                func_name = 'configure_app'
            plugin = importlib.import_module(plugin_module)
            getattr(plugin, func_name)(register_hook)


def register_hook(name, func):
    if 'name' not in current_app.hooks:
        current_app.hooks[name] = []
    current_app.hooks[name].append(func)
