# -*- coding:utf-8 -*-
import os


def get_sports_data():
    """
    使用方式：在某个路由函数如who_view中调用此函数，并在前端手动访问该页面，等待数据处理完毕
    """
    tree = ET.parse('/Users/donghao/Desktop/blogproject/media/data/health_sport.xml')
    # tree = ET.parse('/root/blogproject/media/data/health_sport.xml')
    root = tree.getroot()
    dict_sums = {}

    for neighbor in root.iter('Record'):
        # neighbor.attrib['sourceName'] == '动动' or
        if neighbor.attrib['sourceName'] == 'Lcarusd iphone' and neighbor.attrib['unit'] and neighbor.attrib['unit'] == 'count':

            if neighbor.attrib['sourceName'] == '动动':
                time_ = datetime.strptime(neighbor.attrib['startDate'][0:-6], '%Y-%m-%d %H:%M:%S')
                time_right = datetime(year=2017, month=11, day=20)
                time_left = datetime(year=2017, month=1, day=1)
                if time_ > time_right and time_ > time_left:
                    continue

            dict_sums[neighbor.attrib['startDate']] = {
                "开始时间": neighbor.attrib['startDate'],
                "结束时间": neighbor.attrib['endDate'],
                "步数": neighbor.attrib['value'],
                "数据源": neighbor.attrib['sourceName'],
            }
            print({
                "开始时间": neighbor.attrib['startDate'],
                "结束时间": neighbor.attrib['endDate'],
                "步数": neighbor.attrib['value'],
                "数据源": neighbor.attrib['sourceName'],
            })

    for neighbor in root.iter('Record'):
        if neighbor.attrib['sourceName'] == '动动' and neighbor.attrib['unit'] and neighbor.attrib['unit'] == 'km' and neighbor.attrib['startDate'] in dict_sums:
            dict_sums[neighbor.attrib['startDate']]['公里数'] = neighbor.attrib['value']
            print(neighbor.attrib['startDate'])
            print({'动动公里数': neighbor.attrib['value']})

        if neighbor.attrib['sourceName'] == 'Lcarusd iphone' and neighbor.attrib['unit'] and neighbor.attrib['unit'] == 'km' and neighbor.attrib['startDate'] in dict_sums:
            dict_sums[neighbor.attrib['startDate']]['公里数'] = neighbor.attrib['value']
            print({'iphone公里数':neighbor.attrib['value']})

        if neighbor.attrib['sourceName'] == '动动' and neighbor.attrib['unit'] and neighbor.attrib['unit'] == 'kcal' and neighbor.attrib['startDate'] in dict_sums:
            dict_sums[neighbor.attrib['startDate']]['卡路里'] = neighbor.attrib['value']
            print(neighbor.attrib['startDate'])
            print({'动动卡路里': neighbor.attrib['value']})

    for k, record in dict_sums.items():
        print(record['开始时间'])
        print(record['数据源'])
        temp_step = 0
        temp_step = int(record['步数'])
        sport = Sports.objects.create(
            step =  temp_step,
            start_time = datetime.strptime(record['开始时间'][0:-6], '%Y-%m-%d %H:%M:%S'),
            end_time = datetime.strptime(record['结束时间'][0:-6], '%Y-%m-%d %H:%M:%S'),
            data_source = record['数据源']
        )
        if '公里数' in record:
            sport.km = float(record['公里数'])
            sport.save()
        else:
            sport.km = float(int(record['步数']) * 0.00046)
            sport.save()
        if '卡路里' in record:
            sport.kcal = float(record['卡路里'])
            sport.save()
        # import time
        time.sleep(0.1)

    query_set = Sports.objects.filter(data_source='Lcarusd iphone')
    for obj in query_set:
        time = obj.end_time - obj.start_time
        minute = time.seconds / 60
        hour = round(time.seconds / 60 / 60, 5)
        weight = 69
        try:
            speed = int(400 / ((obj.km * 1000) / minute))
            kcal = weight * hour * 30 / speed
        except ZeroDivisionError:
            kcal = 0
        obj.kcal = kcal
        obj.save()
        print({'卡路里':kcal})

    # 删除所有运动数据
    # Sports.objects.all().delete()



def import_django_environment(project_name):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", '{}.settings'.format(project_name))     # 加载Django环境
    import django   # 引入Django模块
    django.setup()  # 初始化Django环境


def options():

    from blog import models
    print(models.Post.objects.all())
    # 从app当中导入models
    # do something...


if __name__ == '__main__':
    # 该脚本只能运行于项目根目录下
    import_django_environment(project_name='blogproject')
    options()
