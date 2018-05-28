#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response
from flask_restful import Resource
from pymongo import MongoClient, UpdateOne
from bson import json_util
from conf import conf_loader as conf
from services.errors import HttpError
import logging
import traceback
from services.helpers.input_helper import (
    check_count,
    check_threshold,
    check_user,
    check_tag,
    check_alert,
    check_page,
    check_sort,
    check_skip,
)
from services.helpers.response_helper import (
    get_alerts_from_result,
)


class Alert(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(
            conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.alerts = self.db.alerts

    def delete(self, alert):
        try:
            alert_id = check_alert(alert)
        except HttpError as e:
            return {}, e.http_code

        try:
            self.alerts.update_one({'_id': alert_id},
                                   {'$set': {'unlisted': True}},
                                   upsert=True)
        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

        return Response(status=204)  # No content

    def put(self, alert):
        data = request.get_json(force=True)

        if not 'tag' in data:
            return {}, 400  # Bad request
        tag = data['tag']

        try:
            tag = check_tag(tag)
            alert_id = check_alert(alert)
        except HttpError as e:
            return {}, e.http_code

        try:
            self.alerts.update_one({'_id': alert_id},
                                   {'$set': {'tag': tag}},
                                   upsert=True)

            # Tag all the previous alerts for that user that weren't
            # tagged before as unlisted

            # Get the user of the given alert
            full_alert = self.alerts.find_one({'_id': alert_id})

            # Get all the listed alerts for that user without explicit tag
            alerts_to_unlist = self.alerts.find(
                {'user': full_alert['user'],
                 'unlisted': {'$exists': False},
                 'timestamp': {'$lt': full_alert['timestamp']},
                 'tag': {'$exists': False} })

            # Bulk update
            upserts = []
            for alert in alerts_to_unlist:
                upserts.append(UpdateOne(
                    {'_id': alert['_id']},
                    {'$set': {'unlisted': True}} ))
            self.alerts.bulk_write(upserts)


        except Exception:
            logging.error(traceback.format_exc())
            return {}, 500

        return Response(status=204)  # No content


class Alerts(Resource):
    def __init__(self, **kwargs):
        self.mongo_client = MongoClient(
            conf.mongo['address'], conf.mongo['port'])
        self.db = self.mongo_client.reddit_early_risk
        self.alerts = self.db.alerts
        self.users = self.db.users

    def get(self):
        count = request.args.get('count', default=25, type=int)
        sort = request.args.get('sort', default='proba', type=str)
        page = request.args.get('page',
                                default=0, type=int)
        tag = request.args.get('tag',
                               default='undefined', type=str)
        skip = request.args.get('skip', default=0, type=int)

        default_min_threshold = 0
        default_max_threshold = None
        if sort == 'proba':
            threshold_type = float
            default_max_threshold = 1
        elif sort == 'timestamp':
            threshold_type = int

        min_threshold = request.args.get('min_threshold',
                                         default=None,
                                         type=threshold_type)
        max_threshold = request.args.get('max_threshold',
                                         default=None, type=threshold_type)

        if min_threshold != None and max_threshold != None:
            return {}, 501

        if min_threshold == None:
            min_threshold = default_min_threshold
            query_type = 'higher'
        elif max_threshold == None:
            max_threshold = default_max_threshold
            query_type = 'lower'

        # Input values control
        try:
            count = check_count(count)
            min_threshold = check_threshold(min_threshold, sort)
            max_threshold = check_threshold(max_threshold, sort, mandatory=False)
            page = check_page(page)
            tag = check_tag(tag)
            sort = check_sort(sort)
            skip = check_skip(skip)
        except HttpError as e:
            return {}, e.http_code

        try:
            mongo_filter = {}

            # Avoid unlisted alerts
            mongo_filter['unlisted'] = {'$exists': False}

            if min_threshold or max_threshold:
                interval_filter = {}
                if min_threshold:
                    interval_filter['$gt'] = min_threshold
                if max_threshold:
                    interval_filter['$lt'] = max_threshold
                if interval_filter:
                    mongo_filter[sort] = interval_filter

            if tag == 'undecided':
                # Avoid other tags
                mongo_filter['tag'] = {'$nin': ['risk', 'riskfree']}
            else:
                mongo_filter['tag'] = {'$eq': tag}

            skip_filter = count * page
            limit_filter = count
            if query_type == 'lower':
                limit_filter += skip
            elif query_type == 'higher':
                skip_filter += skip

            result = self.alerts.find(mongo_filter) \
                .sort([(sort, -1)]).skip(skip_filter).limit(limit_filter)

            alerts = []
            for alert in result:
                try:
                    risk_vector = self.users.find_one(
                        {'nickname': alert['user']})['risk_vector']
                    alert['risk_vector'] = risk_vector
                except KeyError:
                    alert['risk_vector'] = []
                alerts.append(alert)

        except Exception:
            import traceback
            logging.error(traceback.format_exc())
            return {}, 500

        response = get_alerts_from_result(alerts)
        return response, 200
