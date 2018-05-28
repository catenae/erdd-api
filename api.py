#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
from services import alerts, users, documents, meta, stats
from conf import conf_loader as conf

app = Flask(__name__)
CORS(app)

api = Api(app)

kwargs = {}

# Alerts
api.add_resource(alerts.Alert,
    conf.api['base_url'] + '/alerts/<alert>',
    resource_class_kwargs=kwargs)

api.add_resource(alerts.Alerts,
    conf.api['base_url'] + '/alerts',
    resource_class_kwargs=kwargs)

# api.add_resource(alerts.UserAlerts,
#     conf.api['base_url'] + '/alerts/<user>',
#     resource_class_kwargs=kwargs)

# Users
api.add_resource(users.UserRiskVector,
    conf.api['base_url'] + '/users/<user>/risk-vector',
    resource_class_kwargs=kwargs)

# Dataset
api.add_resource(documents.TaggedPosts,
    conf.api['base_url'] + '/posts/<tag>.json',
    resource_class_kwargs=kwargs)

# Comments
api.add_resource(documents.UserComments,
    conf.api['base_url'] + '/comments/<user>',
    resource_class_kwargs=kwargs)

# Submissions
api.add_resource(documents.UserSubmissions,
    conf.api['base_url'] + '/submissions/<user>',
    resource_class_kwargs=kwargs)

# Meta
api.add_resource(meta.Meta,
    conf.api['base_url'] + '/meta/<attribute>')

# Stats
api.add_resource(stats.RealTime,
    conf.api['base_url'] + '/stats/real-time',
    resource_class_kwargs=kwargs)

api.add_resource(stats.TotalUsers,
    conf.api['base_url'] + '/stats/total-users',
    resource_class_kwargs=kwargs)

api.add_resource(stats.TotalSubmissions,
    conf.api['base_url'] + '/stats/total-submissions',
    resource_class_kwargs=kwargs)

api.add_resource(stats.TotalComments,
    conf.api['base_url'] + '/stats/total-comments',
    resource_class_kwargs=kwargs)


if __name__ == '__main__':
    app.run(host=conf.api['bind_address'],
            port=conf.api['port'])
