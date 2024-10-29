from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from lists.models import UserList

READING = "r"
COMPLETED = "c"
TO_READ = "t"
QUOTE = "q"
NOTE = "n"


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Book(models.Model):
    bookid = models.CharField(max_length=20, unique=True)  # google bookid
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    published = models.CharField(max_length=30)
    isbn = models.CharField(max_length=30)
    pages = models.CharField(max_length=5)
    language = models.CharField(max_length=2)
    description = models.TextField()
    imagesize = models.CharField(max_length=2, default="1")
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name="categories")

    @property
    def title_and_authors(self):
        return f"{self.title} ({self.authors})"

    @property
    def url(self):
        return f"{settings.DOMAIN}/books/{self.bookid}"

    def __str__(self):
        return f"{self.id} {self.bookid} {self.title}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}('{self.id}', "
            f"'{self.bookid}', '{self.title}', '{self.authors}', "
            f"'{self.publisher}', '{self.published}', '{self.isbn}', "
            f"'{self.pages}', '{self.language}', '{self.description}')"
        )


class Search(models.Model):
    term = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    inserted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

    class Meta:
        verbose_name_plural = "searches"


class UserBook(models.Model):
    READ_STATUSES = (
        (READING, "I am reading this book"),
        (COMPLETED, "I have completed this book"),
        (TO_READ, "I want to read this book"),  # t of 'todo'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=READ_STATUSES, default=COMPLETED)
    favorite = models.BooleanField(default=False)
    completed = models.DateTimeField(default=timezone.now)
    booklists = models.ManyToManyField(UserList, related_name="booklists")
    inserted = models.DateTimeField(auto_now_add=True)  # != completed
    updated = models.DateTimeField(auto_now=True)

    @property
    def done_reading(self):
        return self.status == COMPLETED

    def __str__(self):
        return f"{self.user} {self.book} {self.status} {self.completed}"

    class Meta:
        # -favorite - False sorts before True so need to reverse
        ordering = ["-favorite", "-completed", "-id"]


class BookNote(models.Model):
    NOTE_TYPES = (
        (QUOTE, "Quote"),
        (NOTE, "Note"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    userbook = models.ForeignKey(
        UserBook, on_delete=models.CASCADE, blank=True, null=True
    )
    type_note = models.CharField(max_length=1, choices=NOTE_TYPES, default=NOTE)
    description = models.TextField()
    public = models.BooleanField(default=False)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    @property
    def quote(self):
        return self.type_note == QUOTE

    @property
    def type_note_label(self):
        for note, label in self.NOTE_TYPES:
            if note == self.type_note:
                return label.lower()
        return None

    def __str__(self):
        return f"{self.user} {self.userbook} {self.type_note} {self.description} {self.public}"


class Badge(models.Model):
    books = models.IntegerField()
    title = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.books} -> {self.title}"


class BookConversion(models.Model):
    """Cache table to store goodreads -> Google Books mapping"""

    goodreads_id = models.CharField(max_length=20)
    googlebooks_id = models.CharField(max_length=20, null=True, blank=True)
    inserted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goodreads_id} -> {self.googlebooks_id}"


class ImportedBook(models.Model):
    """Cache table for preview goodreads import data"""

    title = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    reading_status = models.CharField(max_length=20)
    date_completed = models.DateTimeField()
    book_status = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.title}"
