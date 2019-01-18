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


@python_2_unicode_compatible
class Seek(models.Model):
    name = models.CharField(verbose_name=u'发布人', max_length=100)
    content = models.TextField(verbose_name='内容')
    show_time = models.DateTimeField(verbose_name='显示时间')
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    modified_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)


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
    image = models.ImageField(default='', upload_to='img/%Y/%m', verbose_name='图片', max_length=900, null=True, blank=True)

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


@python_2_unicode_compatible
class RequestInfo(models.Model):
    # TODO：ip定位误差范围缩小-geoip
    ip_address = models.GenericIPAddressField(verbose_name=u'IP地址')
    area = models.CharField(verbose_name=u'用户位置', max_length=250, default='', null=True, blank=True)
    operator = models.CharField(verbose_name=u'运营商', max_length=250, default='', null=True, blank=True)
    request_time = models.DateTimeField(verbose_name=u'请求时间', auto_now_add=True)
    request_path = models.CharField(verbose_name=u'请求路径', max_length=250, default='', null=True, blank=True)
    device = models.CharField(verbose_name=u'设备品牌', max_length=250, default='', null=True, blank=True)
    device_model = models.CharField(verbose_name=u'设备型号', max_length=250, default='', null=True, blank=True)
    system = models.CharField(verbose_name=u'操作系统', max_length=250, default='', null=True, blank=True)
    system_version = models.CharField(verbose_name=u'操作系统版本', max_length=250, default='', null=True, blank=True)
    browser = models.CharField(verbose_name=u'浏览器', max_length=250, default='', null=True, blank=True)
    browser_version = models.CharField(verbose_name=u'浏览器版本', max_length=250, default='', null=True, blank=True)
    ua = models.CharField(verbose_name=u'请求UA', max_length=250, default='', null=True, blank=True)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    modified_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

@python_2_unicode_compatible
class Sports(models.Model):
    step = models.IntegerField(verbose_name='步数')
    km = models.FloatField(verbose_name='运动公里数', null=True, blank=True, default=0.0)
    kcal = models.FloatField(verbose_name='消耗卡路里', null=True, blank=True, default=0.0)
    start_time = models.DateTimeField(verbose_name='运动开始时间', unique=True)
    end_time = models.DateTimeField(verbose_name='运动结束时间')
    data_source = models.CharField(verbose_name='数据源', max_length=40)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    modified_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)


