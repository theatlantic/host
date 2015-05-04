from django.conf.urls import include, url
from django.contrib import admin
from articles.views import PreView, StyleView

urlpatterns = [
    url(r'^$', PreView.as_view()),
    url(r'^styles/$', StyleView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
]
