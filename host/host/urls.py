from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib import admin
from articles.views import PreView, StyleView, ExportView

urlpatterns = [
    url(r'^$', PreView.as_view()),
    url(r'^export/$', ExportView.as_view()),
    url(r'^styles/$', StyleView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
] + static.static(settings.STATIC_PATH, document_root=settings.STATIC_ROOT)
