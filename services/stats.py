#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_restful import Resource
from pymongo import MongoClient
from conf import conf_loader as conf
from bson import json_util
import logging
import traceback


def _load_kwargs(instance, kwargs):
    instance.mongo_client = MongoClient(
        conf.mongo['address'], conf.mongo['port'])
    instance.db = instance.mongo_client.reddit_early_risk

class RealTime(Resource):
    def __init__(self, **kwargs):
        _load_kwargs(self, kwargs)
        self.stats = self.db.stats

    def get(self):
        try:
            result = self.stats.find_one({'group': 'real_time'})
            response = { 'texts_second': result['texts_second'],
                         'users_second': result['users_second'] }
            return response, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

class TotalUsers(Resource):
    def __init__(self, **kwargs):
        _load_kwargs(self, kwargs)
        self.users = self.db.users

    def get(self):
        try:
            count = self.users.count()
            return {'count': count}, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

class TotalSubmissions(Resource):
    def __init__(self, **kwargs):
        _load_kwargs(self, kwargs)
        self.submissions = self.db.submissions

    def get(self):
        try:
            count = self.submissions.count()
            return {'count': count}, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

class TotalComments(Resource):
    def __init__(self, **kwargs):
        _load_kwargs(self, kwargs)
        self.comments = self.db.comments

    def get(self):
        try:
            count = self.comments.count()
            return {'count': count}, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500
