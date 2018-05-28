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
    check_count,
    check_threshold,
    check_user,
    check_thing_id,
    check_dataset_tag,
    check_page,
)
from services.helpers.response_helper import (
    get_comments_from_result,
    get_submissions_from_result,
    get_posts_from_result,
)


class TaggedPosts(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(
            conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.alerts = self.db.alerts
        self.users = self.db.users
        self.posts = {'submissions': self.db.submissions,
                      'comments': self.db.comments}

    # IMPROVE, VERY INEFFICIENT
    def get(self, tag):
        try:
            tag = check_dataset_tag(tag)
        except HttpError as e:
            return {}, e.http_code

        try:
            posts = {}

            # All the available posts
            if tag == 'all':
                result = self.users.find()
                for user in result:
                    user = user['nickname']
                    posts[user] = {}
                    for post_type in ['submissions', 'comments']:
                        if not post_type in posts[user]:
                            posts[user][post_type] = []

                        result2 = self.posts[post_type].find({'author': user})\
                            .sort([('proba', -1)])

                        posts[user][post_type].append(
                            get_posts_from_result(result2, post_type))

            # Tagged posts
            elif tag in ['risk', 'riskfree']:
                users = {}

                query = {'tag': tag}

                # Avoid also unlisted alerts
                query['unlisted'] = {'$exists': False}

                result = self.alerts.find(query).sort([('timestamp', -1)])
                for alert in result:
                    # Not already seen user (already ordered by timestamp)
                    if alert['user'] not in users:
                        users[alert['user']] = {'last_submission': alert['last_submission'],
                                                'last_comment': alert['last_comment'],
                                                'timestamp': alert['timestamp']}

                # Recuperar textos para cada usuario anteriores a last_comment, last_id
                for user, alert in users.items():
                    posts[user] = {}
                    for post_type in ['submissions', 'comments']:
                        if not post_type in posts[user]:
                            posts[user][post_type] = []

                        if alert['last_' + post_type[:-1]] == None:
                            continue

                        # Only the posts contained by the last alert
                        query = {'author': user,
                                 post_type[:-1] + '_id':
                                 {'$lte': alert['last_' + post_type[:-1]]}}
                        result = self.posts[post_type].find(
                            query).sort([('proba', -1)])

                        posts[user][post_type].append(
                            get_posts_from_result(result, post_type))
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

        return posts, 200


class UserSubmissions(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(
            conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.submissions = self.db.submissions

    def get(self, user):
        """ Returns the last count submissions of an user given a minimum
        probability threshold. Ordered by probability.
        """

        try:
            result = _get_posts_result(user,
                                       'submission',
                                       request.args,
                                       self.submissions)
            response = get_submissions_from_result(result)
            return response, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500


class UserComments(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(
            conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.comments = self.db.comments

    def get(self, user):
        """
        Returns the last count comments of an user given a minimum
        probability threshold. Ordered by probability.
        """
        try:
            result = _get_posts_result(user,
                                       'comment',
                                       request.args,
                                       self.comments)
            response = get_comments_from_result(result)
            return response, 200
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500


def _get_posts_result(user, post_type, request_args, collection):
    last_id = request_args.get('last_id', default=None, type=str)
    count = request_args.get('count', default=25, type=int)
    min_threshold = request_args.get('min_threshold',
                                     default=0, type=float)
    max_threshold = request_args.get('max_threshold',
                                     default=1, type=float)
    page = request_args.get('page', default=0, type=int)

    try:
        count = check_count(count)
        min_threshold = check_threshold(min_threshold)
        max_threshold = check_threshold(max_threshold)
        user = check_user(user)
        last_id = check_thing_id(last_id, False)
        page = check_page(page)
    except HttpError as e:
        return {}, e.http_code

    query = {
        'author': user,
        'proba': {
            '$gte': min_threshold,
            '$lte': max_threshold
        }
    }

    if last_id:
        query[post_type + '_id'] = {
            '$lte': last_id
        }

    result = collection.find(query).sort([('proba', -1)]) \
        .limit(count) \
        .skip(page * count)
    return result
