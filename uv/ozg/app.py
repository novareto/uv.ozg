"""Main module."""

from fanstatic import Resource, Library
from uvcreha.browser.views import View
from uvcreha.app import browser
from uv.ozg import TEMPLATES
from uvcreha import jsonschema



library = Library('uv.ozg', 'static')


def ozg_docs():
    alts = []
    for key, versions in jsonschema.documents_store.items():
        if versions:
            latest = versions.get()
            alts.append((
                f'{key}.{latest.number}',
                latest.value.get('title', key)
            ))
    return alts



@browser.register("/ozg")
class TestView(View):

    template = TEMPLATES["ozg_overview.pt"]

    def GET(self):
        return dict(request=self.request, docs=ozg_docs())


