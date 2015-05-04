import os
import re

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

from lxml import html
import requests

from articles.models import Article, Annotation


class_number_re = re.compile(r"([a-z]+)\d{1}")


class Command(BaseCommand):
    help = "Scrape host and import it and its annotations"

    def _find_annotations(self, tree, parent):
        onclick_elements = tree.xpath("//a[@onclick]")
        url_match = re.compile(r"window.open\('(.+?)'")
        for element in onclick_elements:
            annotation_path = url_match.findall(element.attrib["onclick"])[0]

            broken_paths = [
                "/200504-wallace/58c.mhtml",
                "/200504-wallace/58d.mhtml",
                "/200504-wallace/67d.mhtml",
            ]

            # Rather than fixing this bug, I'm just working around it.
            if annotation_path in broken_paths:
                annotation_path = "/static/coma/html%s" % annotation_path

            annotation_url = "%s%s" % ("http://www.theatlantic.com", annotation_path)
            annotation_resp = requests.get(annotation_url)

            annotation_tree = html.fromstring(annotation_resp.content)
            first_paragraph = annotation_tree.xpath("//p[1]")[0]

            first_paragraph.attrib['class'] = class_number_re.sub(r"\1", first_paragraph.attrib['class'])

            annotation = Annotation.objects.create(parent=parent,
                                                   text=html.tostring(first_paragraph))

            del element.attrib['onclick']
            del element.attrib['target']

            try:
                element.attrib['class'] += " annotation-link"
                element.attrib['class'] = class_number_re.sub(r"\1", element.attrib['class'])
            except KeyError:
                element.attrib['class'] = "annotation-link"

            element.attrib['data-annotation'] = str(annotation.pk)

            self._find_annotations(first_paragraph, annotation)

        parent.text = html.tostring(tree)
        parent.save()

    def handle(self, *args, **kwargs):
        call_command("flush", "--noinput")

        article_file = os.path.join(settings.BASE_DIR, "data", "article.html")
        article_contents = open(article_file).read()

        article = Article.objects.create(text=article_contents)
        article_tree = html.fragment_fromstring(article.text,
                                                create_parent="div")

        self._find_annotations(article_tree, article)
