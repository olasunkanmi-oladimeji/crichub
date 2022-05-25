from django.contrib import admin
from core.models import Post,Comment,Contact
# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)