#!/usr/bin/env python
# -*- coding: utf-8 -*-

class HttpError(Exception):
    def __init__(self, http_code):
        self.http_code = http_code
