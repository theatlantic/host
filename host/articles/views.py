from django.views.generic.base import TemplateView

from lxml import html

from .models import Article, Annotation


class PreView(TemplateView):
    template_name = "index.html"

    def _process_annotations(self, text):
        text_tree = html.fromstring(text)

        annotation_links = text_tree.xpath("//a[@data-annotation]")

        if annotation_links:
            inserted_annotations = []
            annotation_links.reverse()
            for link in annotation_links:
                annotation_id = int(link.attrib['data-annotation'])

                if annotation_id < 0:
                    continue

                if annotation_id in inserted_annotations:
                    continue
                inserted_annotations += [annotation_id]

                annotation = Annotation.objects.get(pk=annotation_id)

                annotation_text = self._process_annotations(annotation.text)
                annotation_tree = html.fromstring(annotation_text)

                annotation_tree.tail = link.tail
                link.tail = ""

                parent_elem = link.getparent()
                parent_elem.insert(parent_elem.index(link) + 1, annotation_tree)

        return html.tostring(text_tree)

    def get_article_content(self):
        article = Article.objects.all()[0]
        return self._process_annotations(article.text)

    def get_context_data(self, **kwargs):
        context = super(PreView, self).get_context_data(**kwargs)
        context['article'] = self.get_article_content()
        return context


class ExportView(PreView):
    template_name = "export.html"


class StyleView(TemplateView):
    template_name = "styles.html"
