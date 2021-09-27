"""Main module."""

import pathlib
import orjson
import logging
from fanstatic import Resource, Library
from uvcreha.browser import Page, routes
from uv.ozg import TEMPLATES
import reiter.versioning.store


library = Library('uv.ozg', 'static')


ozg_store = reiter.versioning.store.Store()


def load_content_types(path: pathlib.Path):
    for f in path.iterdir():
        if f.suffix == '.json':
            with f.open('r') as fd:
                schema = orjson.loads(fd.read())
                key = schema.get('id', f.name)
                version = schema.pop('$version', None)
                ozg_store.add(key, schema, version=version)
                logging.info(f'loading {key} : {str(f.absolute())}.')


def ozg_docs():
    alts = []
    for key, versions in ozg_store.items():
        if versions:
            latest = versions.get()
            alts.append((
                f'{key}.{latest.identifier}',
                latest.value.get('title', key)
            ))
    return alts



@routes.register("/ozg")
class TestView(Page):

    template = TEMPLATES["ozg_overview.pt"]

    def GET(self):
        return dict(request=self.request, docs=ozg_docs())
