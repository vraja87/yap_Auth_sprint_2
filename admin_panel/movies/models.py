import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(verbose_name=_('genre_name'), max_length=255)
    description = models.TextField(verbose_name=_('genre_description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"

        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(verbose_name=_('full_name'), max_length=255)

    class Gender(models.TextChoices):
        MALE = 'MALE', _('male')
        FRMALE = 'FEMALE', _('female')

    gender = models.CharField(verbose_name=_('gender'),
                              max_length=64,
                              choices=Gender.choices,
                              null=True,
                              blank=True,
                              )

    class Meta:
        db_table = "content\".\"person"

        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


#
class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(verbose_name=_('title_film'), max_length=255)
    description = models.TextField(verbose_name=_('film_description'), blank=True, null=True)
    creation_date = models.DateField(verbose_name=_('creation_date'), blank=True, null=True)
    rating = models.FloatField(verbose_name=_('rating'), blank=True,
                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    certificate = models.CharField(max_length=512, blank=True, verbose_name=_('certificate'))
    file_path = models.FileField(verbose_name=_('file'), blank=True, null=True, upload_to='movies/')

    class FilmType(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV = 'tv_show', _('tv_show')

    type = models.CharField(verbose_name=_('type'), max_length=128, choices=FilmType.choices, default=FilmType.MOVIE)

    genres = models.ManyToManyField(Genre, through='GenreFilmwork', verbose_name=_('Genres'))
    persons = models.ManyToManyField(Person, through='PersonFilmwork', verbose_name=_('Persons'))

    class Meta:
        db_table = "content\".\"film_work"

        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')

    def __str__(self):
        return self.title


class PersonFilmwork(UUIDMixin):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('Person'))
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE, verbose_name=_('Filmwork'))
    created = models.DateTimeField(auto_now_add=True)

    class RoleType(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    role = models.CharField(verbose_name=_('role'),
                            max_length=128,
                            choices=RoleType.choices,
                            default=RoleType.ACTOR,
                            null=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = ['person', 'film_work', 'role']
        verbose_name = _('PersonFilmwork')
        verbose_name_plural = _('PersonFilmworks')


class GenreFilmwork(UUIDMixin):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name=_('Genre'))
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE, verbose_name=_('Filmwork'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = ['genre', 'film_work']
        verbose_name = _('GenreFilmwork')
        verbose_name_plural = _('GenreFilmworks')
