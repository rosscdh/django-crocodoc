# -*- coding: utf-8 -*-
"""
Data Providers for the webhook tests
"""

CROCODOC_COMMENT_CREATE = [{"uuid": "65814418-d47b-cee9-988f-370c248faa90", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "owner": "1,Ross C", "type": "point", "event": "annotation.create"}, {"content": "test", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "uuid": "32c6fd5d-551c-45f8-4c93-908b34923868", "owner": "1,Ross C", "event": "comment.create"}]
#
# a reply is denoted by the "to" field
#
CROCODOC_COMMENT_REPLY = [[{"uuid": "1ad40181-605c-0747-8dc5-5cacf8b3faa9", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "content": "kinda nice", "to": "6,Alex Halliday", "owner": "1,Ross C", "event": "comment.create"}]]
CROCODOC_COMMENT_DELETE = [[{"content": "This is a comment that is being deleted", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "uuid": "8e267fc1-16c3-d882-1d9a-29b8def996fa", "owner": "2,Test Lawyer", "event": "comment.delete"}, {"uuid": "13c7d7a9-9b8c-002d-b76c-73f8ec1c5af1", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "owner": "2,Test Lawyer", "type": "point", "event": "annotation.delete"}]]

CROCODOC_ANNOTATION_HIGHLIGHT = [{"uuid": "114e0875-2f3f-2cb4-2516-fe464895ceaf", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "salary is \\u00a360k per annum. Salary", "owner": "1,Ross C", "type": "highlight", "event": "annotation.create"}]
CROCODOC_ANNOTATION_STRIKEOUT = {}

CROCODOC_ANNOTATION_TEXTBOX = [{"uuid": "86941091-97cb-43b0-4e2a-28a5457eb8da", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "fdafasfsddsa", "owner": "1,Ross C", "type": "textbox", "event": "annotation.create"}]
CROCODOC_ANNOTATION_DELETE = [[{"content": "This is a comment annotation that is being deleted", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "uuid": "70fd0eb5-e516-eb6f-3dee-bad36037e9ee", "owner": "2,Test Lawyer", "event": "comment.delete"}, {"uuid": "72e403d4-5f5d-ee4e-0824-5416f89b472c", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "owner": "2,Test Lawyer", "type": "point", "event": "annotation.delete"}]]

CROCODOC_ANNOTATION_DRAWING = {}