from django.contrib import admin
from . import models
# Register your models here.
#admin.site.register(models.Book)
#admin.site.register(models.BookInstance)
admin.site.register(models.Genre)
#admin.site.register(models.Author)
admin.site.register(models.Language)

class BookInstanceInline(admin.TabularInline):
    model = models.BookInstance
    extra = 0

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    #search_fields = ('title', 'author')
    inlines = [BookInstanceInline]

@admin.register(models.BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'status', 'due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('id', 'book')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        })
    )

class BookInline(admin.TabularInline):
    model = models.Book
    extra = 0
    raw_id_fields = ('language',)

@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]