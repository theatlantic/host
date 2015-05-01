from django.views.generic.base import TemplateView

from .models import Article


class PreView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(PreView, self).get_context_data(**kwargs)
        context['article'] = Article.objects.all()[0]
        return context
