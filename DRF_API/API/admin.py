from django.contrib import admin

from .models import *


class TopicAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'syllabus', 'question_number', 'question_payment')
    search_fields = ['subject__type', 'id', 'syllabus']
    date_hierarchy = 'date'
    raw_id_fields = ("subject",)

class SingleQuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'question', 'mark')
    raw_id_fields = ("topic",)

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Topic, TopicAdmin)
admin.site.register(SingleQuestion, SingleQuestionAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(UserAnswerSheet)
admin.site.register(AnswerSheet)
admin.site.register(ImageAnswer)
admin.site.register(UserMark)
