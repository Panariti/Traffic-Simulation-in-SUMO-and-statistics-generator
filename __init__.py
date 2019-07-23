#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from app.main.scheduler import Scheduler
from app.database import DB

def create_app(config):
    app = Flask(__name__)
    DB.init()
    scheduler = Scheduler(seconds=900)
    with app.app_context():
        scheduler.start_scheduler()
    register_blueprints(app)
    return app


def register_blueprints(app):
    from app.main import blueprint as main_api
    app.register_blueprint(main_api)