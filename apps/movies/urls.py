from django.conf.urls import include, url
from movies import views
urlpatterns = [
    url(r'^base/', views.BaseView.as_view(), name="base"),
    url(r'^$', views.IndexView.as_view(), name="index"),  # 配置首页路由
    url(r'^comedy/', views.ComedyView.as_view(), name="comedy"),  # 跳转电影分类详情
]
