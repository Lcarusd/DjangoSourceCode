from django.conf.urls import url

from . import views
from django.views.static import serve
from blogproject.settings import MEDIA_ROOT


app_name = 'blog'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='categorys'),
    url(r'^category/$', views.category_list, name='category'),
    url(r'^who/$', views.who_view, name='who'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^phone/$', views.phone_view, name='phone'),
    # 处理 media 信息，用于图片获取
    url(r'^media/(?P<path>.*)', serve, {"document_root":MEDIA_ROOT}),
]
