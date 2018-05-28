#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_restful import Resource
from pymongo import MongoClient
from conf import conf_loader as conf
from bson import json_util
from services.errors import HttpError
import logging
import traceback
from services.helpers.input_helper import (
    check_user,
)
from services.helpers.response_helper import (
    get_risk_vector_from_result
)

class UserRiskVector(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.users = self.db.users

    def get(self, user):
        try:
            user = check_user(user)
        except HttpError as e:
            return {}, e.http_code

        try:
            result = self.users.find_one({ "nickname": user })
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

        if not result:
            return {}, 404

        response = get_risk_vector_from_result(result)
        return response, 200
