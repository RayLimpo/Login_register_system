
# 发送邮件调试脚本
import  os

from django.core.mail import  EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'loginSite.settings'

if __name__ == '__main__':
    subject,from_email,to = '测试邮件','707******@163.com','**@sina.com'
    text_content = "欢迎访问"
    html_content = '<p>欢迎访问<a href="http://www.baidu.com" target=blank>www.baidu.com</a>，这里是百度...</p>'
    msg =EmailMultiAlternatives(subject,text_content,from_email,[to])
    msg.attach_alternative(html_content,'text/html')
    msg.send()