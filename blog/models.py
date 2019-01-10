from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from django.utils.html import format_html
import django.utils.timezone as timezone
from markdownx.utils import markdownify
from markdownx.models import MarkdownxField

def get_foo():
    return User.objects.get_or_create(id=1)[0].id


# python_2_unicode_compatible 装饰器用于兼容 Python2
@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Post(models.Model):
    post_state = (
        (0, '草稿'),
        (1, '发布'),
    )

    title = models.CharField(verbose_name=u'文章标题', max_length=80, unique=True)
    body = MarkdownxField(verbose_name=u'文章正文')
    show_time = models.DateField(verbose_name=u'显示时间', default = timezone.now)
    created_time = models.DateTimeField(verbose_name='文章创建时间', auto_now_add=True)
    modified_time = models.DateTimeField(verbose_name='文章修改时间', auto_now=True)
    views = models.PositiveIntegerField(verbose_name='阅读量', default=0, editable=False)
    # 一篇文章只能对应一个分类，但是一个分类下可以有多篇文章
    category = models.ForeignKey(Category, related_name = "category", verbose_name='文章分类')
    author = models.ForeignKey(User, verbose_name='作者', default=get_foo)
    # 0为草稿，1为发布
    state = models.IntegerField(
        choices=post_state,
        default=1,
        verbose_name='文章状态',
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']

    # Create a property that returns the markdown instead
    @property
    def formatted_markdown(self):
        return markdownify(self.body)

    # 自定义 get_absolute_url 方法
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    # 设置文章发布状态属性值的颜色
    def state_color(self):
        color = None
        if self.state == 0:
            color = 'red'
            self.state = "草稿"
        elif self.state == 1:
            color = 'green'
            self.state = "发布"
        return format_html('<span style="color: {}">{}</span>', color, self.state, )

    # 文章阅读量+1
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
