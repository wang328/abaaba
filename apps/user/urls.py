from user import views
from django.conf.urls import url

urlpatterns = [
    url(r"^login/", views.LoginView.as_view(), name="login"),  # 配置登录路由
    url(r'^register/', views.RegisterView.as_view(), name='register'),  # 配置注册的路由
    url(r'^active/(?P<token>.*)/', views.ActiveView.as_view(), name="active"),  # 用户激活
    url(r"^forgetpwd/", views.ForgetPwdView.as_view(), name="forgetpwd"),  # 忘记密码
    url(r'^updata/(?P<token>.*)/', views.UpdataPwdView.as_view(), name='updata'),  # 修改密码
    url(r"^updatasucc/", views.UpdataSuccView.as_view(), name='updatasucc'),  # 修改密码成功
]
