from django.db import models
from django.utils.translation import ugettext_lazy as _


class NameModel(models.Model):
    """Абстрактная модель добавляющая название."""

    name = models.CharField(
        _('Название'),
        unique=True,
        max_length=150,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
