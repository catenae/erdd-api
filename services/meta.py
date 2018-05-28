#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_restful import Resource

class Meta(Resource):
    def get(self, attribute):

        if attribute == 'version':
            return 'v0.1-alpha', 200

        return '', 404
