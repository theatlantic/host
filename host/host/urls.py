from django.conf.urls import include, url
from django.contrib import admin
from articles.views import PreView

urlpatterns = [
    # Examples:
    url(r'^$', PreView.as_view()),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
