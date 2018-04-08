"""
一组请求处理器，返回要合并到模板上下文中的字典。 每个函数都将请求对象作为其唯一参数，并返回一个字典以添加到上下文中。

这些参数来自DjangoTemplates后端配置的'context_processors'选项，并由RequestContext使用。
"""

from __future__ import unicode_literals

from django.conf import settings
from django.middleware.csrf import get_token
from django.utils import six
from django.utils.encoding import smart_text
from django.utils.functional import lazy


def csrf(request):
    """
    提供CSRF标记的上下文处理器，或者视图装饰器或中间件未提供的字符串“NOTPROVIDED”
    """
    def _get_val():
        token = get_token(request)
        if token is None:
            # 为了能够在错误配置的情况下提供调试信息，我们使用一个sentinel值而不是返回一个空的字典。
            return 'NOTPROVIDED'
        else:
            return smart_text(token)
    _get_val = lazy(_get_val, six.text_type)

    return {'csrf_token': _get_val()}


def debug(request):
    """
    Returns context variables helpful for debugging.
    """
    context_extras = {}
    if settings.DEBUG and request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        context_extras['debug'] = True
        from django.db import connection
        # Return a lazy reference that computes connection.queries on access,
        # to ensure it contains queries triggered after this function runs.
        context_extras['sql_queries'] = lazy(lambda: connection.queries, list)
    return context_extras


def i18n(request):
    from django.utils import translation

    context_extras = {}
    context_extras['LANGUAGES'] = settings.LANGUAGES
    context_extras['LANGUAGE_CODE'] = translation.get_language()
    context_extras['LANGUAGE_BIDI'] = translation.get_language_bidi()

    return context_extras


def tz(request):
    from django.utils import timezone

    return {'TIME_ZONE': timezone.get_current_timezone_name()}


def static(request):
    """
    Adds static-related context variables to the context.

    """
    return {'STATIC_URL': settings.STATIC_URL}


def media(request):
    """
    Adds media-related context variables to the context.

    """
    return {'MEDIA_URL': settings.MEDIA_URL}


def request(request):
    return {'request': request}
