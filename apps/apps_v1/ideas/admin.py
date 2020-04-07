from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Idea)
admin.site.register(IdeaComment)
admin.site.register(IdeaLike)