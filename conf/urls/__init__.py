from importlib import import_module
import warnings

from django.core.urlresolvers import (RegexURLPattern,
                                      RegexURLResolver, LocaleRegexURLResolver)
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.utils.deprecation import RemovedInDjango110Warning


__all__ = ['handler400', 'handler403', 'handler404',
           'handler500', 'include', 'patterns', 'url']

handler400 = 'django.views.defaults.bad_request'
handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'


def include(arg, namespace=None, app_name=None):
    if app_name and not namespace:
        raise ValueError('Must specify a namespace if specifying app_name.')

    if isinstance(arg, tuple):
        # 可调用返回一个命名空间提示
        if namespace:
            raise ImproperlyConfigured(
                '无法覆盖提供名称空间的动态模块的名称空间')
        urlconf_module, app_name, namespace = arg
    else:
        # 没有名称空间提示 - 使用手动提供的名称空间
        urlconf_module = arg

    if isinstance(urlconf_module, six.string_types):
        urlconf_module = import_module(urlconf_module)
    patterns = getattr(urlconf_module, 'urlpatterns', urlconf_module)

    # 确保我们可以遍历模式（没有这个，一些测试用例会中断）。
    if isinstance(patterns, (list, tuple)):
        for url_pattern in patterns:

            # 测试包含中是否使用了LocaleRegexURLResolver;
            # 这应该抛出一个错误，因为这是不允许的！
            if isinstance(url_pattern, LocaleRegexURLResolver):
                raise ImproperlyConfigured(
                    '在包含的URLconf中使用i18n_patterns是不允许的。')

    return (urlconf_module, app_name, namespace)


def patterns(prefix, *args):
    warnings.warn(
        'django.conf.urls.patterns() is deprecated and will be removed in '
        'Django 1.10. Update your urlpatterns to be a list of '
        'django.conf.urls.url() instances instead.',
        RemovedInDjango110Warning, stacklevel=2
    )
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list


def url(regex, view, kwargs=None, name=None, prefix=''):
    if isinstance(view, (list, tuple)):
        # include(...) 处理。
        urlconf_module, app_name, namespace = view
        return RegexURLResolver(regex, urlconf_module, kwargs, app_name=app_name, namespace=namespace)
    else:
        if isinstance(view, six.string_types):
            warnings.warn(
                'Support for string view arguments to url() is deprecated and '
                'will be removed in Django 1.10 (got %s). Pass the callable '
                'instead.' % view,
                RemovedInDjango110Warning, stacklevel=2
            )
            if not view:
                raise ImproperlyConfigured(
                    'Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return RegexURLPattern(regex, view, kwargs, name)
