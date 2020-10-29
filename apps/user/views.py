import re

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from user.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import View
from abaaba import settings
from celery_tasks.tasks import send_regiser_active_email,send_updata_pwd_email
from itsdangerous import TimedJSONWebSignatureSerializer as tjs

""" 用户注册类  """


class RegisterView(View):
    def get(self, request):
        """  显示注册页面  """
        return render(request, "register.html")

    def post(self, request):
        """  处理首页中注册部分的表单信息 """
        # 1. 接收表单中的数据
        username = request.POST.get("username")
        userpwd = request.POST.get("userpwd")
        cpwd = request.POST.get("usercpwd")
        email = request.POST.get("useremail")
        allow = request.POST.get("allow")

        # print(username, userpwd, cpwd, email)
        # 2. 校验表单中的数据
        if not all([username, userpwd, email]):
            # 由于注册 与 登录的功能和首页放置在一起  所以希望报错的功能能够以弹窗的形式展现出来
            return render(request, "index.html", {"msg": "数据不完整"})
        # # 3. 校验邮箱是否合法
        if not re.match(r"[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, "register.html", {"msg": "邮箱格式不正确"})
        if userpwd != cpwd:
            return render(request, "register.html", {"msg": "两次密码输入不一致"})
        if allow != "on":
            return render(request, "register.html", {"msg": "请勾选协议"})
        # 4. 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在时
            user = None
        if user:
            return render(request, "register.html", {"msg": "用户名已存在"})
        # 5. 业务处理（向mysql中添加一条数据）
        user = User.objects.create_user(username, email, username)
        # #   我们不希望刚刚创建的用户处于激活状态 而是希望通过邮箱或者短信验证码进行激活
        user.is_active = 0  # 0 表示未激活 1代表已经激活
        user.save()
        # todo 当注册成功以后，往邮箱里发送一个邮件，单击邮件进行激活
        # todo 我们希望 用户单击这个地址可以激活用户：ttp;//127.0.0.1:8000/user/active/用户id
        # 用户id不能为明文
        ss = tjs(settings.SECRET_KEY, 3600)
        info = {"user_id": user.id}
        token = ss.dumps(info).decode()  # 加密id并去掉b''

        # todo 发送邮件
        # todo 将同步代码剪切走以后 换成下面的异步方法来进行发送邮件
        send_regiser_active_email.delay(email, username, token)

        #  6. 返回应答
        #     重定向到首页
        return redirect(reverse("movies:index"))


"""  激活用户   """


class ActiveView(View):
    """   进行用户的激活 """

    def get(self, request, token):
        '''  用户激活程序  '''
        # 进行解密，获取需要激活的用户信息
        ss = tjs(settings.SECRET_KEY, 3600)
        token = token.encode()
        try:
            info = ss.loads(token)  # 这里应该是user的某一个id user_id :id
            # 根据解密的用户id查询数据库
            user = User.objects.get(id=info.get("user_id"))
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except Exception as e:
            return HttpResponse("链接已过期")


"""  登录类  """


class LoginView(View):
    def get(self, request):
        """  登录功能  """
        # 先判断用户以前有没有记住过用户名
        if "username" in request.COOKIES:
            # 表示以前记住过用户名了
            username = request.COOKIES.get("username")
            checked = "checked"
        else:
            # 表示以前没有记住过用户名
            username = ""
            checked = ""
        return render(request, "login.html", {"username": username, "checked": checked})

    def post(self, request):
        '''  登录校验  '''

        # 1. 接收参数
        username = request.POST.get("username")
        pwd = request.POST.get("userpwd")
        remember = request.POST.get("remember")
        # 2. 校验参数
        if not all([username, pwd]):
            return render(request, "login.html", {"msg": "输入数据不完整"})
        # 3. 业务处理
        user = authenticate(username=username, password=pwd)  # django中提供的认证系统
        if user is not None:
            # 说明用户名与密码是匹配I的
            if user.is_active:
                # 说明该用户是处于激活状态的
                login(request, user)
                # todo 获取地址栏中？后面的next参数的值
                next = request.GET.get("next", reverse("movies:index"))

                res = redirect(next)
                # 判断登录的用户有没有记住过用户名

                if remember == "on":
                    # 记住用户名了
                    res.set_cookie("username", username, max_age=7 * 24 * 3600)
                else:
                    # 没有记住用户名,删除cookie
                    res.delete_cookie("username")
                return res
            else:
                # 说明此用户不是处于激活状态的
                return render(request, "login.html", {"msg": "请到邮箱激活用户"})
        else:
            # 用户名和密码是不匹配的
            return render(request, "login.html", {"msg": "用户名或密码不正确"})
        # 4. 返回应答  应答已在上面的操作中输出

class ForgetPwdView(View):
    def get(self,request):
        return render(request,"password.html")

    def post(self,request):
        # 接收用户名
        username = request.POST.get("username")
        if not all([username]):
            return render(request, "password.html", {"msg": "用户名必填"})
        # 业务处理==根据用户名查询邮箱，再向邮箱内发送邮件
        try:
            user = User.objects.get(username=username)
            email = user.email  # 取它email字段的值
            user_id = user.id  # 取它的id字段的值
            # 对id字段进行加密
            ss = tjs(settings.SECRET_KEY, 3600)
            info = {"user_id": user_id}
            token = ss.dumps(info).decode()
            send_updata_pwd_email.delay(email, username, token)
            return HttpResponse("请到邮箱中修改密码")
        except User.DoesNotExist as e:
            return render(request, "password.html", {"msg": "用户名不存在"})


class UpdataPwdView(View):
    def get(self, request, token):
        # 解密
        ss = tjs(settings.SECRET_KEY, 3600)
        token = token.encode()
        try:
            info = ss.loads(token)
            user = User.objects.get(id=info.get("user_id"))
            return render(request, "password_2.html", {"user_id": user.id})
        except Exception as e:
            return HttpResponse("链接已过期")

    def post(self, request, token):
        # 接收修改后的密码
        user_id = request.POST.get("user_id")
        print(user_id)
        pwd = request.POST.get("username")
        print(pwd)
        cpwd = request.POST.get("usercpwd")
        print(cpwd)
        # 校验参数
        if not all([pwd, cpwd]):
            return render(request, "password_2.html", {"msg": "数据输入不完整"})
        if pwd != cpwd:
            return render(request, "password_2.html", {"msg": "两次密码不一致"})
        # 业务处理
        u = User.objects.get(id=user_id)
        print(u)
        u.set_password(pwd)
        u.save()

        return redirect(reverse("user:updatasucc"))


class UpdataSuccView(View):
    def get(self,request):
        return render(request,"password_3.html")