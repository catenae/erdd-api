#!/usr/bin/env python
# -*- coding: utf-8 -*-

from services.errors import HttpError
import logging
import traceback
from bson.objectid import ObjectId


def check_count(count, mandatory=True):
    if mandatory and count == None:
        raise HttpError(422) # Unprocessable Entity
    if count > 100:
        count = 100
    elif count < 1 and count != 0:
        raise HttpError(422) # Unprocessable Entity
    return count

def check_threshold(threshold, sort='proba', mandatory=True):
    if mandatory and threshold == None:
        raise HttpError(422) # Unprocessable Entity
    elif not mandatory and threshold == None:
        return
    else:
        if sort == 'proba' and (threshold <= 1 or threshold >= 0):
            return threshold
        elif sort == 'timestamp' and threshold >= 0: # Before 1970
            return threshold
    raise HttpError(422) # Unprocessable Entity

def check_user(user, mandatory=True):
    if mandatory and user == None:
        raise HttpError(422) # Unprocessable Entity
    return user

def check_tag(tag, mandatory=True):
    allowed_tags = ['undecided', 'risk', 'riskfree']
    if mandatory and tag == None or tag not in allowed_tags:
        raise HttpError(422) # Unprocessable Entity
    return tag

def check_dataset_tag(tag, mandatory=True):
    allowed_tags = ['all', 'risk', 'riskfree']
    if mandatory and tag == None or tag not in allowed_tags:
        raise HttpError(422) # Unprocessable Entity
    return tag

def check_alert(alert, mandatory=True):
    if mandatory and alert == None:
        raise HttpError(422) # Unprocessable Entity
    try:
        alert = ObjectId(alert)
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HttpError(422) # Unprocessable Entity
    return alert

def check_thing_id(thing_id, mandatory=True):
    if mandatory and thing_id == None:
        raise HttpError(422) # Unprocessable Entity
    return thing_id

def check_page(page, mandatory=True):
    if mandatory and page == None:
        raise HttpError(422) # Unprocessable Entity
    return page

def check_sort(sort, mandatory=True):
    allowed_sorts = ['proba', 'timestamp']
    if mandatory and sort == None or sort not in allowed_sorts:
        raise HttpError(422) # Unprocessable Entity
    return sort

def check_skip(skip, mandatory=True):
    if mandatory and skip == None:
        raise HttpError(422) # Unprocessable Entity
    return skip
