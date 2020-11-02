from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View
from user.models import User
from django.contrib.auth import authenticate,login,logout


# Create your views here.

class IndexView(View):
    def get(self, request):

        # 判断用户有没有登陆
        user = request.user
        # print(user)

        context = 0
        user_info = None

        # 检验用户名是否存在
        if user.is_authenticated():
            context = 1
            user_info = User.objects.get(username=user)


        return render(request, 'index.html', {"context":context,"user_info":user_info})

class BaseView(View):
    def get(self, request):
        return render(request, 'base_index_comedy.html')


class ComedyView(View):
    def get(self, request):
        return render(request, 'comedy.html')



