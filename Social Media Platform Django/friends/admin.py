from django.contrib import admin
from .models import Block, Follow, FriendRequest

admin.site.register([Block, Follow, FriendRequest])
