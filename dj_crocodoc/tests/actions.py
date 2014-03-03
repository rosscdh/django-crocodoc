# -*- coding: utf-8 -*-
"""
unit Test the signal classes
"""
import unittest

import dj_crocodoc.services as crocodoc_services
import dj_crocodoc.signals as crocodoc_signals

class CrocodocBaseTest(unittest.TestCase):
    subject = None
    expected_signal = None
    expected_verb = None
    expected_deleted_verb = None

    def setUp(self):
        if self.subject is not None:
            self.subject = self.subject()

    def test_signal(self):
        if self.subject is not None:
            self.assertEqual(self.subject.signal, self.expected_signal)

    def test_verb(self):
        if self.subject is not None:
            self.assertEqual(self.subject.verb, self.expected_verb)

    def test_deleted_verb(self):
        if self.subject is not None:
            self.assertEqual(self.subject._deleted_verb, self.expected_deleted_verb)


class CrocodocCommentCreateEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocCommentCreateEvent
    expected_signal = crocodoc_signals.crocodoc_comment_create
    expected_verb = 'Commented on an Document'


class CrocodocCommentDeleteEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocCommentDeleteEvent
    expected_signal = crocodoc_signals.crocodoc_comment_delete
    expected_verb = 'Deleted a Commented on an Document'


class CrocodocAnnotationHighlightEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocAnnotationHighlightEvent
    expected_signal = crocodoc_signals.crocodoc_annotation_highlight
    expected_verb = 'Hilighted some text on an Document'
    expected_deleted_verb = 'Deleted a Hilighted of some text on an Document'


class CrocodocAnnotationStrikeoutEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocAnnotationStrikeoutEvent
    expected_signal = crocodoc_signals.crocodoc_annotation_strikeout
    expected_verb = 'Struck out some text on an Document'
    expected_deleted_verb = 'Deleted the Strikeout of some text on an Document'


class CrocodocAnnotationTextboxEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocAnnotationTextboxEvent
    expected_signal = crocodoc_signals.crocodoc_annotation_textbox
    expected_verb = 'Added a text element on an Document'
    expected_deleted_verb = 'Deleted a text element on an Document'


class CrocodocAnnotationDrawingEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocAnnotationDrawingEvent
    expected_signal = crocodoc_signals.crocodoc_annotation_drawing
    expected_verb = 'Added a drawing element on an Document'
    expected_deleted_verb = 'Deleted a drawing element on an Document'


class CrocodocAnnotationPointEventTest(CrocodocBaseTest):
    subject = crocodoc_services.CrocodocAnnotationPointEvent
    expected_signal = crocodoc_signals.crocodoc_annotation_point
    expected_verb = 'Added a point element to a Document'
    expected_deleted_verb = 'Deleted a point element on an Document'
