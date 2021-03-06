## 项目依赖

Django==1.10
<br>
Python==3.5。

## 在本地运行项目

1. 克隆项目到本地

   打开命令行，进入到保存项目的文件夹，输入如下命令：

   ```
   git clone https://github.com/Lcarusd/blog.git
   ```

2. 创建并激活虚拟环境

   在命令行进入到保存虚拟环境的文件夹，输入如下命令创建并激活虚拟环境：
   如果不想使用虚拟环境，可以跳过这一步。

   ```
   virtualenv blog_env

   # windows
   blog_env\Scripts\activate

   # linux
   source blog_env/bin/activate
   ```

3. 安装项目依赖

   如果使用了虚拟环境，确保激活并进入了虚拟环境，在命令行进入项目所在的 blog 文件夹，运行如下命令：

   ```
   pip install -r requirements.txt
   ```

4. 迁移数据库

   在上一步所在的位置运行如下命令迁移数据库：

   ```
   python manage.py migrate
   ```

5. 创建后台管理员账户

   在上一步所在的位置运行如下命令创建后台管理员账户

   ```
   python manage.py createsuperuser
   ```

6. 运行开发服务器

   在上一步所在的位置运行如下命令开启开发服务器：

   ```
   python manage.py runserver
   ```

   在浏览器输入：127.0.0.1:8000

7. 进入后台发布文章

   在浏览器输入：127.0.0.1:8000/admin

   使用第 5 步创建的后台管理员账户登录


#### 导出数据 导入数据
python manage.py dumpdata appname > appname.json
python manage.py loaddata appname.json 

#### 生成requirements.txt文件
pip freeze > requirements.txt

#### shell命令行
python manage.py shell

#### 清空数据库
python manage.py flush 

#### 数据库命令行
python manage.py dbshell 

#### 修改用户密码
python manage.py changepassword username 

#### 查看更多命令
python manage.py 


##### uwsgi启动关闭命令
uwsgi --ini uwsgi.ini 
uwsgi --stop uwsgi.pid


#### 常用命令
python manage.py runserver

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic

python manage.py migrate --run-syncdb
python manage.py migrate --fake blog

python manage.py createsuperuser

root@188.131.177.190:/root/


