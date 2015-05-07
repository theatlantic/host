import os
import re

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

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
            color = element.attrib['class']
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
            annotation_content = annotation_tree.xpath("//font[@class='covertype']")[0]
            del annotation_content[len(annotation_content) - 1]  # Delete the last paragraph.

            annotation, _ = Annotation.objects.get_or_create(
                parent_id=parent.id,
                parent_ctype=ContentType.objects.get_for_model(parent),
                original_text=html.tostring(annotation_content)
            )

            annotation_content.attrib['class'] = class_number_re.sub(r"\1", color)
            annotation_content.attrib['class'] += " annotation"

            annotation_content.tag = "span"

            annotation_content.attrib['data-annotation'] = str(annotation.pk)
            annotation_content.attrib['id'] = "annotation%s" % annotation.pk
            annotation_content.attrib['style'] = "display: none;"

            for paragraph in annotation_content.xpath("//p"):
                paragraph.tag = "span"

            # Replace all the paragraphs with non-paragraphs.
            for table in annotation_content.xpath("//table"):
                font_tag = table.xpath("//font[@class='covertype']")[0]
                font_tag.tag = "span"
                font_tag.attrib['class'] = "blockquote"
                font_tag.tail = table.tail

                parent_elem = table.getparent()
                parent_elem.insert(parent_elem.index(table), font_tag)
                parent_elem.remove(table)

            annotation.text = html.tostring(annotation_content)
            annotation.save()

            del element.attrib['onclick']
            del element.attrib['target']

            element.attrib["href"] = "%s#annotation%s" % (settings.ORIGINAL_URL, annotation.pk)

            try:
                element.attrib['class'] += " annotation-link"
                element.attrib['class'] = class_number_re.sub(r"\1", element.attrib['class'])
            except KeyError:
                element.attrib['class'] = "annotation-link"

            element.attrib['data-annotation'] = str(annotation.pk)

            self._find_annotations(annotation_content, annotation)

        parent.text = html.tostring(tree)
        parent.save()

    def handle(self, *args, **kwargs):
        os.remove(settings.DATABASES['default']['NAME'])
        call_command("migrate")
        call_command("flush", "--noinput")

        article_file = os.path.join(settings.BASE_DIR, "data", "article.html")
        article_contents = open(article_file).read()

        article = Article.objects.create(text=article_contents)
        article_tree = html.fragment_fromstring(article.text,
                                                create_parent="div")

        self._find_annotations(article_tree, article)
