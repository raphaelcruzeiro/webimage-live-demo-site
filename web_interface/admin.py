# -*- coding: utf-8 -*-
from django.contrib import admin
from models import PreviewRequest

class PreviewRequestAdmin(admin.ModelAdmin):
    search_fields = ['email', 'url']
    date_hierarchy = 'requested_on'
    list_display = ['img', 'url', 'email', 'requested_on', 'generated', 'sent']
    list_filter = ['generated', 'sent']

admin.site.register(PreviewRequest, PreviewRequestAdmin)