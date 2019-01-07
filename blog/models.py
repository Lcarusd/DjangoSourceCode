import markdown
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from django.utils.html import strip_tags


# python_2_unicode_compatible 装饰器用于兼容 Python2
@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Post(models.Model):

    # 文章标题
    title = models.CharField(u'文章标题', max_length=80)

    # 文章正文
    body = models.TextField(u'文章正文')

    # 文章的创建时间和最后一次修改时间
    show_time = models.DateTimeField(u'展示时间')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField()


    # 文章摘要
    excerpt = models.CharField(u'文章摘要', max_length=200, blank=True)

    # 阅读量
    views = models.PositiveIntegerField(default=0)

    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    # 文章作者
    author = models.ForeignKey(User)

    def __str__(self):
        return self.title

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_time']

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)
