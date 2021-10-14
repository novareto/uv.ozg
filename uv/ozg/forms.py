from uuid import uuid4
from reha.prototypes.events import UserLoggedInEvent
from uvcreha import events
from uvcreha.browser import routes
from reiter.form import trigger
from reha.prototypes.workflows.file import file_workflow
from reha.prototypes.workflows.document import document_workflow
from uvcreha.browser.document import DefaultDocumentEditForm, DocumentEdit
from jsonschema_wtforms import schema_fields
from uvcreha.browser.form import JSONForm
from .app import ozg_store


OZG = "ozg"


@events.subscribe(UserLoggedInEvent)
def create_ozg(event):
    ct, crud = event.request.get_crud("file")
    try:
        filedata = {
            "uid": event.user.uid,
            "az": OZG,
            "mnr": "mnr",
            "vid": "vid",
            "state": file_workflow.states.validated.name,
        }
        crud.create(filedata)
    except BaseException as exc:
        pass


class OZGDefaultDocumentEditForm(DefaultDocumentEditForm):
    @property
    def title(self):
        ct, version = self.content_type.split(".", 1)
        return ct

    def setupForm(self, formdata=None):
        ct, version = self.content_type.split(".", 1)
        schema = ozg_store.get(ct, version)  # , version)
        form = JSONForm.from_schema(schema.value)
        form.process(data={}, formdata=formdata)
        return form

    def get_fields(self):
        name, version = self.content_type.rsplit(".", 1)
        schema = ozg_store.get(name, version)
        return schema_fields(schema.value)

    @trigger("Speichern", css="btn btn-primary", order=10)
    def save(self, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}

        ct, crud = self.request.get_crud("document")
        docdata = {
            "docid": str(uuid4()),
            "az": OZG,
            "uid": self.request.user.uid,
            "state": document_workflow.states.sent.name,
            "content_type": self.request.route.params["content_type"],
            "item": form.data,
        }
        crud.create(docdata)
        return self.redirect("/")


@routes.register("/ozg/{content_type}", methods=["GET", "POST"], name="ozg.edit")
def ozg_edit_dispatch(request, **params):
    form = DocumentEdit.get(params["content_type"], OZGDefaultDocumentEditForm)
    form.content_type = params["content_type"]
    return form(request, **params)()
