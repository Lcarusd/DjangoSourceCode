"""
用于从INSTALLED_APPS包中的“模板”目录加载模板的包装器。
"""

import io

from django.core.exceptions import SuspiciousFileOperation
from django.template.base import TemplateDoesNotExist
from django.template.utils import get_app_template_dirs
from django.utils._os import safe_join

from .base import Loader as BaseLoader


class Loader(BaseLoader):
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """
        当附加到“template_dirs”中的每个目录时，
        返回到“template_name”的绝对路径。 
        出于安全原因，不包含在模板目录之内的任何路径将从结果集中排除。
        """
        if not template_dirs:
            template_dirs = get_app_template_dirs('templates')
        for template_dir in template_dirs:
            try:
                yield safe_join(template_dir, template_name)
            except SuspiciousFileOperation:
                # 加入的路径位于此template_dir的外部（它可能在另一个内部，所以这不是致命的）。
                pass

    def load_template_source(self, template_name, template_dirs=None):
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                with io.open(filepath, encoding=self.engine.file_charset) as fp:
                    return fp.read(), filepath
            except IOError:
                pass
        raise TemplateDoesNotExist(template_name)
