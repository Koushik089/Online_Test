from django.contrib import admin
from .models import AdminUser, Question

admin.site.register(AdminUser)
admin.site.register(Question)
