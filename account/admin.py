
# Register your models here.
from django.contrib import admin

from .models import  Company,User, Card,Member




# Register your models here.
admin.site.register(User)
admin.site.register(Company)
admin.site.register(Card)
admin.site.register(Member)
