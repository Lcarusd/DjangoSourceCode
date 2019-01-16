from django.contrib import admin
from .models import Post, Category, Seek, RequestInfo

# https://blog.csdn.net/youand_me/article/details/78831494

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'show_time', 'category', 'author', 'state_color']
    list_filter = ['show_time', 'category', 'state']
    search_fields = ('title',)
    list_per_page = 10000

class SeekAdmin(admin.ModelAdmin):
    list_display = ['name', 'content', 'show_time']
    search_fields = ('content',)
    ordering = ['-show_time', ]
    list_per_page = 10000

class RequestInfoAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'area', 'request_time', 'request_path', 'device', 'system', 'browser']
    ordering = ['-request_time', ]



admin.site.site_header = 'Lcarusd Blog Admin'
admin.site.site_title = 'Lcarusd Blog Admin'
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Seek, SeekAdmin)
admin.site.register(RequestInfo, RequestInfoAdmin)
