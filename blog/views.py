import markdown
from markdown.extensions.toc import TocExtension
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.text import slugify

from .models import Post, Category

# https://code.ziqiangxuetang.com/django/django-queryset-api.html
# https://www.jianshu.com/p/923b89ec18eb


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10000

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["post_list"] = Post.objects.filter(state=1).order_by("-views")
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
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


def category_list(request):
    category_list = Category.objects.all()
    return render(request, 'option/category.html', context={'category_list': category_list})


class CategoryView(ListView):

    def get(self, request, pk):
        category_post = Category.objects.get(pk=int(pk)).category.all().filter(state__gt=0)
        return render(
            request,
            'blog/index.html',
            context={'post_list': category_post})


def who_view(request):
    return render(request, 'option/who.html')


def contact(request):
    return render(request, 'option/contact.html',)


def phone_view(request):
    post_list = Post.objects.filter(state=1).order_by("-views")
    return render(request, 'phone.html', context={"post_list":post_list})
