#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_alerts_from_result(result):
    alerts = []
    for item in result:
        if not 'tag' in item:
            item['tag'] = 'undecided'
        alerts.append({
            'id': str(item['_id']),
            'user': item['user'],
            'priority': item['priority'],
            'proba': item['proba'],
            'type': item['type'],
            'last_submission': item['last_submission'],
            'last_comment': item['last_comment'],
            'timestamp': item['timestamp'],
            'risk_vector': item['risk_vector'],
            'tag': item['tag']
        })
    return alerts

def get_posts_from_result(result, post_type, omit_author=True):
    if post_type == 'submissions':
        return get_submissions_from_result(result, omit_author)
    elif post_type == 'comments':
        return get_comments_from_result(result, omit_author)

def get_comments_from_result(result, omit_author=False):
    """ Get a list of comments from a pymongo result. Author is omitted
    by default.
    """
    comments = []
    for item in result:
        comment = {
            'comment_id': item['comment_id'],
            'submission_id': item['submission_id'],
            'subreddit_id': item['subreddit_id'],
            'submission_title': item['submission_title'],
            'content': item['content'],
            'timestamp': item['timestamp']
        }
        if 'proba' in item:
            comment['proba'] = item['proba']
        if not omit_author:
            comment['author'] = item['author']

        comments.append(comment)
    return comments

def get_submissions_from_result(result, omit_author=False):
    """ Get a list of submissions from a pymongo result. Author is omitted
    by default.
    """
    submissions = []
    for item in result:
        submission = {
            'submission_id': item['submission_id'],
            'subreddit_id': item['subreddit_id'],
            'submission_title': item['submission_title'],
            'content': item['content'],
            'timestamp': item['timestamp']
        }
        if 'proba' in item:
            submission['proba'] = item['proba']
        if not omit_author:
            submission['author'] =  item['author']

        submissions.append(submission)
    return submissions

def get_risk_vector_from_result(result):
    if 'risk_vector' in result:
        return result['risk_vector']
    return []
