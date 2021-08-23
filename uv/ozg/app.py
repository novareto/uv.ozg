"""Main module."""

from fanstatic import Resource, Library
from uvcreha.browser.views import View
from uvcreha.app import browser
from uv.ozg import TEMPLATES


library = Library('uv.ozg', 'static')


@browser.register("/ozg")
class TestView(View):

    template = TEMPLATES["ozg_overview.pt"]

    def GET(self):
        return dict(request=self.request)


