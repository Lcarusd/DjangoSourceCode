import os

def import_django_environment(project_name):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", '{}.settings'.format(project_name))     # 加载Django环境
    import django   # 引入Django模块
    django.setup()  # 初始化Django环境


def options():

    from blog import models
    print(models.Post.objects.all())
    # 从app当中导入models
    # do something...


# if __name__ == '__main__':
# 该脚本只能运行于项目根目录下
import_django_environment(project_name='blogproject')
options()