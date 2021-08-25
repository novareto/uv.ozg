from horseman.http import HTTPError
from datetime import datetime
from uuid import uuid4
from uvcreha.events import UserLoggedInEvent
from uvcreha.app import browser, events
from reiter.form import trigger
from uvcreha import jsonschema, contenttypes
from uvcreha.workflow import file_workflow, document_workflow
from uvcreha.browser.document import DefaultDocumentEditForm, DocumentEdit
from jsonschema_wtforms import schema_fields


OZG = "ozg"


@events.subscribe(UserLoggedInEvent)
def create_ozg(event):
    content_type = contenttypes.registry['file']
    filedata = {
        "uid": event.user.id,
        "az": OZG,
        "mnr": "mnr",
        "vid": "vid",
        "state": file_workflow.states.validated.name,
    }
    crud = content_type.get_crud(event.request.app)
    try:
        crud.create(filedata, event.request)
    except HTTPError as exc:
        if int(exc.status) != 409:
            # Already exist
            raise



class OZGDefaultDocumentEditForm(DefaultDocumentEditForm):

    def get_fields(self):
        name, version = self.content_type.rsplit(".", 1)
        schema = jsonschema.documents_store.get(name, version)
        return schema_fields(schema.value)

    @trigger("Speichern", css="btn btn-primary", order=10)
    def save(self, data):
        form = self.setupForm(formdata=data.form)
        import pdb; pdb.set_trace()
        if not form.validate():
            return {"form": form}
      
        content_type = contenttypes.registry['document']
        crud = content_type.get_crud(self.request.app)
        docdata = {
            "docid": str(uuid4()),
            "az": OZG,
            "uid": self.request.user.id,
            "creation_date": datetime.now(),
            "state": document_workflow.states.sent.name,
            "content_type": self.request.route.params["content_type"],
            "item": form.data
        }
        document = crud.create(docdata, self.request)
        return self.redirect("/")


@browser.register(
    '/ozg/{content_type}', methods=['GET', 'POST'], name='ozg.edit')
def ozg_edit_dispatch(request, **params):
    form = DocumentEdit.get(
        params["content_type"],
        OZGDefaultDocumentEditForm
    )
    form.content_type = params["content_type"]
    return form(request, **params)()
