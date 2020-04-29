from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Email(models.Model):
    userid = models.CharField(max_length=50, db_column='UserId')
    address = models.EmailField(max_length=50, db_column='Address')
    role = models.CharField(max_length=50, choices=[('R', 'requestor'), ('A', 'approver')], default='R', db_column='Role')



class Payment(models.Model):
    ordernumber = models.BigIntegerField(primary_key=True, db_column='OrderNumber')
    requestor = models.CharField(max_length=50, db_column='Requestor')
    email = models.ForeignKey(Email, models.SET_NULL, null=True, db_column='Address')
    lastmodified = models.DateTimeField(auto_now=True, null=True, db_column='LastModified')

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, null=True)
    imprint = models.CharField(max_length=200)
    isbn = models.CharField('ISBN', max_length=200)
    genre = models.ManyToManyField('Genre')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ','.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def get_full_name(self):
        return self.first_name + ',' + self.last_name

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class BookInstance(models.Model):
    LOAN_STATUS = [
        ('m', 'Maintainance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    due_back = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=LOAN_STATUS, default='m')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)

    class Meta:
        permissions = [('mark_bookinstance', 'can mark book instance')]

    def __str__(self):
        return f'({self.id}): {self.book.title}'

    def get_status_display(self):
        for s in self.LOAN_STATUS:
            if(s[0]==self.status):
                return s[1]
    
    @property
    def is_overdue(self):
        if self.due_back and date.today()>self.due_back:
            return True
        return False


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
