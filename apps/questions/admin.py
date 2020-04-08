from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionFollow)
admin.site.register(QuestionInvite)
