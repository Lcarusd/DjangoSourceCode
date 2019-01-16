from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.text import slugify

import markdown
from markdown.extensions.toc import TocExtension
from ua_parser import user_agent_parser
import requests
from bs4 import BeautifulSoup

from .models import Post, Category, Seek, RequestInfo

# https://code.ziqiangxuetang.com/django/django-queryset-api.html
# https://www.jianshu.com/p/923b89ec18eb


def get_ip_info_to_func(func):
    def wrapper(request):
        get_ip_info_to_class(request)
        return func(request)
    return wrapper


def get_ip_info_to_class(request):
    ua_string = request.META['HTTP_USER_AGENT']
    parsed_string = user_agent_parser.Parse(ua_string)

    # 获取操作系统与操作系统版本信息
    system_version_list = []
    if parsed_string['os']['major']: system_version_list.append(parsed_string['os']['major'])
    if parsed_string['os']['minor']: system_version_list.append(parsed_string['os']['minor'])
    if parsed_string['os']['patch']: system_version_list.append(parsed_string['os']['patch'])
    if len(system_version_list) == 3:
        system_version_list.insert(1, ".")
        system_version_list.insert(3, ".")
    elif len(system_version_list) == 2:
        system_version_list.insert(1, ".")
    system_version = "".join(system_version_list)
    system = parsed_string['os']['family'] if parsed_string['os']['family'] else ''

    # 获取设备品牌与设备信号信息
    device = parsed_string['device']['family'] if parsed_string['device']['family'] else ''
    if device == 'Other': device = system.split()[0]
    device_model = parsed_string['device']['model'] if parsed_string['device']['model'] else ''

    # 获取浏览器及浏览器版本信息
    browser_version_list = []
    if parsed_string['user_agent']['major']: browser_version_list.append(parsed_string['user_agent']['major'])
    if parsed_string['user_agent']['minor']: browser_version_list.append(parsed_string['user_agent']['minor'])
    if parsed_string['user_agent']['patch']: browser_version_list.append(parsed_string['user_agent']['patch'])
    if len(browser_version_list) == 3:
        browser_version_list.insert(1, ".")
        browser_version_list.insert(3, ".")
    elif len(browser_version_list) == 2:
        browser_version_list.insert(1, ".")
    browser_version = "".join(browser_version_list)
    browser = parsed_string['user_agent']['family'] if parsed_string['user_agent']['family'] else ''

    # 获取请求ip、请求时间、请求路径信息
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        request_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        request_ip = request.META['REMOTE_ADDR']
    request_path = request.path

    # 创建请求记录
    rt = RequestInfo.objects.create(ip_address=request_ip)
    rt.request_path = request_path
    rt.system, rt.system_version = system, system_version
    rt.device, rt.device_model = device, device_model
    rt.browser, rt.browser_version = browser, browser_version
    rt.ua = ua_string
    rt.save()

    # 获取请求源地理位置与运营商信息
    spider_ip_location_and_operator(request_ip, rt)


def spider_ip_location_and_operator(ip, rt):
    query_set = RequestInfo.objects.filter(ip_address=ip)
    if query_set[0].area:
        rt.area = query_set[0].area
        rt.save()
        return

    # 数据库未找到ip位置信息，发起请求查询
    ip_url = "http://ip.t086.com/?ip={0}".format(ip)
    headers = {
        'content-type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    try:
        response = requests.get(ip_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        area = soup.select("#c > div.bar2.f16 > b")[0].string
        rt.area = area
        rt.save()
    except:
        pass


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10000

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["post_list"] = Post.objects.filter(state=1).order_by("-views")
        get_ip_info_to_class(self.request)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        get_ip_info_to_class(request)
        return response     # 视图必须返回一个 HttpResponse 对象

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post


class CategoryView(ListView):
    def get(self, request, pk):
        category_post = Category.objects.get(pk=int(pk)).category.all().filter(state__gt=0)
        get_ip_info_to_class(request)
        return render(request, 'blog/index.html', context={'post_list': category_post})


@get_ip_info_to_func
def category_list(request):
    category_list = Category.objects.all()
    return render(request, 'option/category.html', context={'category_list': category_list})


@get_ip_info_to_func
def seek_view(request):
    seeks = Seek.objects.all().order_by("-show_time")
    return render(request, 'option/seek.html', context={"seeks": seeks})


@get_ip_info_to_func
def who_view(request):
    return render(request, 'option/who.html')


@get_ip_info_to_func
def contact(request):
    return render(request, 'option/contact.html',)


@get_ip_info_to_func
def phone_view(request):
    post_list = Post.objects.filter(state=1).order_by("-views")
    return render(request, 'phone.html', context={"post_list":post_list})
