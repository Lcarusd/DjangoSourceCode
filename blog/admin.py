from django.contrib import admin
from .models import Post, Category, Seek

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


admin.site.site_header = 'Lcarusd Blog Admin'
admin.site.site_title = 'Lcarusd Blog Admin'
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Seek, SeekAdmin)
