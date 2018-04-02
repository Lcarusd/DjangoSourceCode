from __future__ import unicode_literals

import warnings

from django.apps import apps
from django.db import models
from django.db.utils import IntegrityError, OperationalError, ProgrammingError
from django.utils.deprecation import RemovedInDjango110Warning
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class ContentTypeManager(models.Manager):
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        super(ContentTypeManager, self).__init__(*args, **kwargs)
        # 由所有get_for_*方法共享缓存，以加速ContentType检索。
        self._cache = {}

    def get_by_natural_key(self, app_label, model):
        try:
            ct = self._cache[self.db][(app_label, model)]
        except KeyError:
            ct = self.get(app_label=app_label, model=model)
            self._add_to_cache(self.db, ct)
        return ct

    def _get_opts(self, model, for_concrete_model):
        if for_concrete_model:
            model = model._meta.concrete_model
        elif model._deferred:
            model = model._meta.proxy_for_model
        return model._meta

    def _get_from_cache(self, opts):
        key = (opts.app_label, opts.model_name)
        return self._cache[self.db][key]

    def create(self, **kwargs):
        if 'name' in kwargs:
            del kwargs['name']
            warnings.warn(
                "ContentType.name field doesn't exist any longer. Please remove it from your code.",
                RemovedInDjango110Warning, stacklevel=2)
        return super(ContentTypeManager, self).create(**kwargs)

    def get_for_model(self, model, for_concrete_model=True):
        """
        返回给定模型的ContentType对象，并在必要时创建ContentType。 
        查找被缓存，以便后续查找相同的模型不会遇到数据库。
        """
        opts = self._get_opts(model, for_concrete_model)
        try:
            return self._get_from_cache(opts)
        except KeyError:
            pass

        # ContentType条目未在缓存中找到，因此我们继续加载或创建它。
        try:
            try:
                # 我们从get()开始，而不是get_or_create()以使用db_for_read（请参阅＃20401）。
                ct = self.get(app_label=opts.app_label, model=opts.model_name)
            except self.model.DoesNotExist:
                # 在数据库中找不到; 我们继续创建它。这次我们使用get_or_create来处理任何竞争条件(race conditions)。
                ct, created = self.get_or_create(
                    app_label=opts.app_label,
                    model=opts.model_name,
                )
        except (OperationalError, ProgrammingError, IntegrityError):
            # 可以在contenttypes之前迁移单个应用程序，因为它不是必需的初始依赖项（它是contrib！）
            # 对此有一个很好的错误。
            raise RuntimeError(
                "Error creating new content types. Please make sure contenttypes "
                "is migrated before trying to migrate apps individually."
            )
        self._add_to_cache(self.db, ct)
        return ct

    def get_for_models(self, *models, **kwargs):
        """
        给定*模型，返回一个字典映射{model：content_type}。
        """
        for_concrete_models = kwargs.pop('for_concrete_models', True)
        # 最终结果
        results = {}
        # 尚未在缓存中的模型
        needed_app_labels = set()
        needed_models = set()
        needed_opts = set()
        for model in models:
            opts = self._get_opts(model, for_concrete_models)
            try:
                ct = self._get_from_cache(opts)
            except KeyError:
                needed_app_labels.add(opts.app_label)
                needed_models.add(opts.model_name)
                needed_opts.add(opts)
            else:
                results[model] = ct
        if needed_opts:
            cts = self.filter(
                app_label__in=needed_app_labels,
                model__in=needed_models
            )
            for ct in cts:
                model = ct.model_class()
                if model._meta in needed_opts:
                    results[model] = ct
                    needed_opts.remove(model._meta)
                self._add_to_cache(self.db, ct)
        for opts in needed_opts:
            # 这些不在缓存或数据库中，创建它们。
            ct = self.create(
                app_label=opts.app_label,
                model=opts.model_name,
            )
            self._add_to_cache(self.db, ct)
            results[ct.model_class()] = ct
        return results

    def get_for_id(self, id):
        """
        通过ID查找ContentType。 
        使用与get_for_model相同的共享缓存（尽管ContentTypes显然不是由get_by_id实时创建的）。
        """
        try:
            ct = self._cache[self.db][id]
        except KeyError:
            # 这可能会引发一个DoesNotExist; 
            # 这是正确的行为，并将确保只有正确的ctypes存储在缓存字典中。
            ct = self.get(pk=id)
            self._add_to_cache(self.db, ct)
        return ct

    def clear_cache(self):
        """
        清除内容类型缓存。 
        这需要在数据库刷新期间发生，以防止缓存“陈旧”的内容类型ID
        (请参阅django.contrib.contenttypes.management.update_contenttypes以获取调用的位置)
        """
        self._cache.clear()

    def _add_to_cache(self, using, ct):
        """将一个ContentType插入到缓存中。"""
        # 请注意，ContentType对象可能过时; model_class（）将返回None。
        # 因此，这里不需要依赖model._meta.app_label，而只是使用模型字段。
        key = (ct.app_label, ct.model)
        self._cache.setdefault(using, {})[key] = ct
        self._cache.setdefault(using, {})[ct.id] = ct


@python_2_unicode_compatible
class ContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(_('python model class name'), max_length=100)
    objects = ContentTypeManager()

    class Meta:
        verbose_name = _('content type')
        verbose_name_plural = _('content types')
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

    def __str__(self):
        return self.name

    @property
    def name(self):
        model = self.model_class()
        if not model:
            return self.model
        return force_text(model._meta.verbose_name)

    def model_class(self):
        "返回此类内容的Python模型类"
        try:
            return apps.get_model(self.app_label, self.model)
        except LookupError:
            return None

    def get_object_for_this_type(self, **kwargs):
        """
        为给定的关键字参数返回此类型的对象。
        基本上，这是围绕此object_type的get_object（）模型方法的代理。 
        ObjectNotExist异常如果抛出，将不会被捕获，因此调用此方法的代码应该捕获它。
        """
        return self.model_class()._base_manager.using(self._state.db).get(**kwargs)

    def get_all_objects_for_this_type(self, **kwargs):
        """
        为给定的关键字参数返回此类型的所有对象。
        """
        return self.model_class()._base_manager.using(self._state.db).filter(**kwargs)

    def natural_key(self):
        return (self.app_label, self.model)
