from datetime import date

from django.contrib.auth.models import User
from django.db import models


def current_year():
    return date.today().year


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    year = models.IntegerField(default=current_year)
    number_books = models.IntegerField(default=0)
    share = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"{self.user} => {self.number_books} "
            f"(in {self.year} / shared: {self.share})"
        )
