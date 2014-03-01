# -*- coding: utf-8 -*-
from django.views.generic import View
from braces.views import JSONResponseMixin

from .services import CrocdocWebhookService

import logging
logger = logging.getLogger('django.request')


class CrocdocCallbackView(JSONResponseMixin, View):
    """
    Handle the crocdoc callback
    """
    template = None
    json_dumps_kwargs = {'indent': 3}

    def get(self, request, *args, **kwargs):
        context_dict = {
            'message': 'Please Post to this endpoint',
        }
        return self.render_json_response(context_dict)

    def post(self, request, *args, **kwargs):
        # import pdb
        # pdb.set_trace()

        service = CrocdocWebhookService(payload=request.POST.get('payload', '[]'))
        logger.info('recived crocdoc webhook: {json}'.format(json=service.items))

        service.process()
        # for c, i in enumerate(service.items):
        #     logger.info('Item {num} event: {event}'.format(num=c, event=i))

        """
        status: payload
        [{"status": "DONE", "viewable": true, "event": "document.status", "uuid": "a2b9cdc4-50cc-466f-afd9-a37012dd1395"}]'

        comment: payload
        [{"uuid": "65814418-d47b-cee9-988f-370c248faa90", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "owner": "2,Ross C", "type": "point", "event": "annotation.create"}, {"content": "test", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "uuid": "32c6fd5d-551c-45f8-4c93-908b34923868", "owner": "2,Ross C", "event": "comment.create"}]

        ANNOTATION.CREATE

        textbox: payload
        [{"uuid": "86941091-97cb-43b0-4e2a-28a5457eb8da", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "fdafasfsddsa", "owner": "2,Ross C", "type": "textbox", "event": "annotation.create"}]

        highlight: payload
        [{"uuid": "114e0875-2f3f-2cb4-2516-fe464895ceaf", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "salary is \\u00a360k per annum. Salary", "owner": "2,Ross C", "type": "highlight", "event": "annotation.create"}]'

        ANNOTATION.UPDATE

        textbox: payload
        [{"uuid": "86941091-97cb-43b0-4e2a-28a5457eb8da", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "fdafasfsddsa", "owner": "2,Ross C", "type": "textbox", "event": "annotation.create"}]

        highlight: payload
        [{"uuid": "114e0875-2f3f-2cb4-2516-fe464895ceaf", "doc": "b15532bb-c227-40f6-939c-a244d123c717", "page": 1, "content": "salary is \\u00a360k per annum. Salary", "owner": "2,Ross C", "type": "highlight", "event": "annotation.create"}]'

        """
        context_dict = {
            'monkies': 1,
        }

        return self.render_json_response(context_dict)