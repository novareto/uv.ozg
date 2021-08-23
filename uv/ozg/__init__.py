import pathlib
from reiter.application.browser import TemplateLoader


TEMPLATES = TemplateLoader(
    str((pathlib.Path(__file__).parent / "templates").resolve()), ".pt")
