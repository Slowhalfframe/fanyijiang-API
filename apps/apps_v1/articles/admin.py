from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Article)
admin.site.register(ArticleComment)
admin.site.register(ArticleVote)