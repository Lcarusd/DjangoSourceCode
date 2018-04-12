"""
这是函数和“跨越”多层次MVC的类的模块集帮助。换句话说，为了方便起见，这些函数/类引入控制耦合。
"""

import warnings

from django.core import urlresolvers
from django.db.models.base import ModelBase
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect,
)
from django.template import RequestContext, loader
from django.template.context import _current_app_undefined
from django.template.engine import (
    _context_instance_undefined, _dictionary_undefined, _dirs_undefined,
)
from django.utils import six
from django.utils.deprecation import RemovedInDjango110Warning
from django.utils.encoding import force_text
from django.utils.functional import Promise


def render_to_response(template_name, context=None,
                       context_instance=_context_instance_undefined,
                       content_type=None, status=None, dirs=_dirs_undefined,
                       dictionary=_dictionary_undefined, using=None):
    """
    返回一个HttpResponse，其内容填充了传递参数调用django.template.loader.render_to_string（）的结果。
    """
    if (context_instance is _context_instance_undefined and dirs is _dirs_undefined and dictionary is _dictionary_undefined):
        # 没有弃用的参数被传递 - 使用新的代码路径
        content = loader.render_to_string(template_name, context, using=using)

    else:
        # 传递了一些弃用的参数 - 使用遗留代码路径
        content = loader.render_to_string(
            template_name, context, context_instance, dirs, dictionary,
            using=using)

    return HttpResponse(content, content_type, status)


def render(request, template_name, context=None,
           context_instance=_context_instance_undefined,
           content_type=None, status=None, current_app=_current_app_undefined,
           dirs=_dirs_undefined, dictionary=_dictionary_undefined,
           using=None):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    Uses a RequestContext by default.
    """
    if (context_instance is _context_instance_undefined
            and current_app is _current_app_undefined
            and dirs is _dirs_undefined
            and dictionary is _dictionary_undefined):
        # No deprecated arguments were passed - use the new code path
        # In Django 1.10, request should become a positional argument.
        content = loader.render_to_string(
            template_name, context, request=request, using=using)

    else:
        # Some deprecated arguments were passed - use the legacy code path
        if context_instance is not _context_instance_undefined:
            if current_app is not _current_app_undefined:
                raise ValueError('If you provide a context_instance you must '
                                 'set its current_app before calling render()')
        else:
            context_instance = RequestContext(request)
            if current_app is not _current_app_undefined:
                warnings.warn(
                    "The current_app argument of render is deprecated. "
                    "Set the current_app attribute of request instead.",
                    RemovedInDjango110Warning, stacklevel=2)
                request.current_app = current_app
                # Directly set the private attribute to avoid triggering the
                # warning in RequestContext.__init__.
                context_instance._current_app = current_app

        content = loader.render_to_string(
            template_name, context, context_instance, dirs, dictionary,
            using=using)

    return HttpResponse(content, content_type, status)


def redirect(to, *args, **kwargs):
    """
    Returns an HttpResponseRedirect to the appropriate URL for the arguments
    passed.

    The arguments could be:

        * A model: the model's `get_absolute_url()` function will be called.

        * A view name, possibly with arguments: `urlresolvers.reverse()` will
          be used to reverse-resolve the name.

        * A URL, which will be used as-is for the redirect location.

    By default issues a temporary redirect; pass permanent=True to issue a
    permanent redirect
    """
    if kwargs.pop('permanent', False):
        redirect_class = HttpResponsePermanentRedirect
    else:
        redirect_class = HttpResponseRedirect

    return redirect_class(resolve_url(to, *args, **kwargs))


def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.

    Raises a ValueError if klass is not a Model, Manager, or QuerySet.
    """
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, Manager):
        manager = klass
    elif isinstance(klass, ModelBase):
        manager = klass._default_manager
    else:
        if isinstance(klass, type):
            klass__name = klass.__name__
        else:
            klass__name = klass.__class__.__name__
        raise ValueError("Object is of type '%s', but must be a Django Model, "
                         "Manager, or QuerySet" % klass__name)
    return manager.all()


def get_object_or_404(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      queryset.model._meta.object_name)


def get_list_or_404(klass, *args, **kwargs):
    """
    Uses filter() to return a list of objects, or raise a Http404 exception if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    obj_list = list(queryset.filter(*args, **kwargs))
    if not obj_list:
        raise Http404('No %s matches the given query.' %
                      queryset.model._meta.object_name)
    return obj_list


def resolve_url(to, *args, **kwargs):
    """
    返回适合传递参数的URL。

    参数可以是：
    *模型：模型的`get_absolute_url（）`函数将被调用。
    *视图名称，可能带有参数：`urlresolvers.reverse（）`将用于反向解析名称。
    *一个URL，它将按原样返回。
    """
    # 如果它是一个模型，使用get_absolute_url（）
    if hasattr(to, 'get_absolute_url'):
        return to.get_absolute_url()

    if isinstance(to, Promise):
        # 展开惰性实例，因为它会在进一步传递给一些Python函数（如urlparse）时导致问题。
        to = force_text(to)

    if isinstance(to, six.string_types):
        # 处理相对URL
        if any(to.startswith(path) for path in ('./', '../')):
            return to

    # 接下来尝试反向网址解析。
    try:
        return urlresolvers.reverse(to, args=args, kwargs=kwargs)
    except urlresolvers.NoReverseMatch:
        # 如果这是可调用的，请重新加注。
        if callable(to):
            raise
        # 如果这感觉不像像一个URL，重新提高。
        if '/' not in to and '.' not in to:
            raise

    # 最后，回退并假定它是一个URL
    return to
