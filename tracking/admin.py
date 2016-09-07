from django.contrib import admin
from .models import Visitor, BannedIP, UntrackedUserAgent


class VisitorAdmin(admin.ModelAdmin):
    search_fields = ['username']
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
