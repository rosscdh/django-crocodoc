django-crocdoc
==============

Django integration with crocdoc

Use-Case
--------

As an application developer

I want to be able to send a document to crocdoc and generate a url to provide
my users with access to the crocdoc version of my document. So that they may 
comment on make annotations and provide feedback on the document


Using
-----

__settings.py__

```
INSTALLED_APPS = (
    'dj_crocodoc',
)
```


You may also want to include our tests with yours

__test_settings.py__

```
INSTALLED_APPS = INSTALLED_APPS + (
    'dj_crocodoc.tests',
)
```

There are two means of using the system

### As a Service

```
from dj_crocodoc.services import CrocoDocConnectService

# get my object that i want to send to crocodoc for review
document = FakeDocumentObject.objects.create(my_document_field='./test.pdf')

service = CrocoDocConnectService(document_object=document,  # send the full object to the service
                                 app_label='tests',         # need to know which app it is a part of
                                 field_name='my_document_field', # specify the field name that handles the FileObject
                                 upload_immediately=False)  # dont upload it to crocodoc right away (default)

```


__inspect the objects__

```
>>>service.obj
<CrocodocDocument: CrocodocDocument object>
>>>service.is_new
True
```


__get the source object from our crocodoc object__

```
>>>service.obj.source_object
<FakeDocumentObject: FakeDocumentObject object>
```

### As a Signal

```
from dj_crocodoc.signals import send_to_crocodoc

document = FakeDocumentObject.objects.create(my_document_field='./test.pdf')

send_to_crocodoc.send(sender=self,  # the sender of the signal
                      document_object=document, # the object to upload
                      app_label='tests',    # the ap label
                      field_name='my_document_field', # the field that contains the FileObject
                      upload_immediately=True)  # default is true

```