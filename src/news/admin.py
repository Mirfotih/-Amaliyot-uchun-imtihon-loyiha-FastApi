from django.contrib import admin
from news.models import Post, PostComment, PostImage, PostLike, Category

class PostImageInline(admin.TabularInline):
    model = PostImage

@admin.register(Category)
class UserAdminCategory(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Post)
class UserAdminPost(admin.ModelAdmin):
    list_display = ('id', 'title')
    inlines = [PostImageInline]


@admin.register(PostComment)
class UserAdminPostComment(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'comment')


@admin.register(PostImage)
class UserAdminPostImage(admin.ModelAdmin):
    list_display = ('id', 'post')


@admin.register(PostLike)
class UserAdminPostLike(admin.ModelAdmin):
    list_display = ('id', 'user', 'post')
