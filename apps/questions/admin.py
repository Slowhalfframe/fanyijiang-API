from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QAComment)
admin.site.register(QuestionFollow)
admin.site.register(QuestionInvite)
admin.site.register(QAComment)
admin.site.register(ACVote)