from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (['name'])
    list_filter = (['name'])
    search_fields = ('name', 'id')
    list_per_page = 25


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmworkInline,)
    list_display = ('full_name', 'created', 'modified')
    search_fields = ('full_name', 'id')
    list_per_page = 25


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = ('title', 'type', 'creation_date', 'rating', 'created', 'modified')
    list_filter = (['type'])
    search_fields = ('title', 'description', 'id', 'type')
    list_prefetch_related = ('persons', 'genres')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(*self.list_prefetch_related)
