from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from .import models
from .import forms

import hashlib
import datetime
from django.conf import settings

def hash_code(s, salt='login'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def make_confirm_string(user):
    print('该方法用于创建确认码对象')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code

def send_email(email,code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自系统注册确认邮件'
    text_content = "感谢您注册，这里是Django学习注册系统邮件"
    html_content ='''<p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.baidu.com</a>，这里是百度...恭喜注册成功！</p>
    <p>请点击链接完成注册！</p>
    '''.format('127.0.0.1:8002',code,settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    print('注册系统发送邮件完成。。。')


def index(request):
    pass
    return render(request,'login/index.html')
'''
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        message = "所有字段都必须填写！"
        if username and password:
            username = username.strip()
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    return redirect('/index/')
                else:
                    message = '密码不正确'
            except:
               message = '用户名不存在'
        return render(request, 'login/login.html', {"message": message})
    return render(request,'login/login.html')
'''#form表单优化后：
def login(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message ='请检查填写内容'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            captcha = login_form.cleaned_data['captcha']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:                      # 增加用户邮件确认校验是否通过
                    message = '该用户还未通过确认'
                    return render(request,'login/login.html',locals())
                if user.password == hash_code(password):         # 哈希值和数据库内的值进行比对
                    request.session['is_login']=True
                    request.session['user_id']=user.id
                    request.session['user_name']=user.name
                    return redirect('/index/')
                else:
                    message = '密码错误！'
            except:
                message = '用户不存在！'
        return render(request,'login/login.html',locals())
    login_form =forms.UserForm()
    return render(request,'login/login.html',locals())

def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查注册信息'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:
                message = '两次密码输入不一致'
                return render(request,'login/register.html',locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  #判断用户名唯一
                    message = '用户名已存在，请重新输入'
                    return render(request,'login/register.html',locals())
                same_name_email = models.User.objects.filter(email=email)
                if same_name_email: #判断邮箱唯一
                    message = '邮箱已被注册，请重新选择'
                    return  render(request,'login/register.html',locals())
                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex =sex
                new_user.save()

                code = make_confirm_string(new_user)                    # 调用创建确认码方法，调发邮件方法，跳转确认页面
                send_email(email,code)
                message = '请前往注册邮箱，进行邮件确认...!'
                return  render(request,'login/confirm.html',locals())
    register_form = forms.RegisterForm()
    return render(request,'login/register.html',locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    #del request.session['is_login']
    #del request.session['user_id']
    #del request.session['user_name']
    return redirect("/index/")

# 添加 confirm 确认视图——用户注册成后，进入邮件确认注册。
def user_confirm(request):
    import pytz
    print('处理用户邮件确认请求。。。')
    code =  request.GET.get('code',None)
    message = ''
    try:
        confirm  = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求！'
        return  render(request,'login/confirm.html',locals())

    create_time = confirm.create_time
    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    if now > create_time +  datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期，请重新注册！'
        return  render(request,'login/confirm.html',locals())
    else:
        confirm.user.has_confirmed =  True
        confirm.user.save()
        confirm.delete()
        message = '已确认，请使用账户登录！'
        return  render(request,'login/confirm.html',locals())

