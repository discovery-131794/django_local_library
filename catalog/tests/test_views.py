from django.test import Client, TestCase
from catalog.models import Author, Book, BookInstance, Genre, Language
from catalog.views import AuthorView
from django.urls import reverse, resolve
from urllib.parse import urlparse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from datetime import date,timedelta
import uuid

class AuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        num_of_authors = 7
        for num in range(num_of_authors):
            Author.objects.create(first_name=str(num))
        cls.client = Client(enforce_csrf_checks=True)

    def test_view_url(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_pattern(self):
        response = self.client.get(reverse('show-authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_response_template(self):
        response = self.client.get('/catalog/authors/')
        self.assertTemplateUsed(response, 'all_author.html')

    def test_view_response_context(self):
        response = self.client.get('/catalog/authors/')
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['author_list']), 2)
        self.assertEqual(response.context['page_obj'].number, 1)
    
    def test_view_response_pagination(self):
        response = self.client.get('/catalog/authors/?page=4')
        self.assertEqual(len(response.context['author_list']), 1)
        self.assertEqual(response.resolver_match.func.__name__,urlparse('/catalog/authors/')[2])

class MyBookTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='John', password='secret')
        test_user2 = User.objects.create_user(username='Alice', password='secret')
        test_user1.save()
        test_user2.save()
        print('test setup')

        test_author = Author.objects.create(first_name='test', last_name='author')
        test_genre = Genre.objects.create(name='fiction')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='test_book', author=test_author, imprint='version-2020', isbn='isbn',language=test_language)
        test_book.genre.add(test_genre)

        num_of_instance  = 30
        for num in range(num_of_instance):
            if num % 2 == 0:
                BookInstance.objects.create(due_back=date.today()+timedelta(days=num),status='o',book=test_book,borrower=test_user1)
            else:
                BookInstance.objects.create(status='m',book=test_book)

        self.client = Client()

    def test_login_user_view(self):
        self.client.login(username='John',password='secret')
        response = self.client.get('/catalog/mybook/',follow=True)
        self.assertEqual(str(response.context['user']),'John')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'mybook.html')

    def test_anonymous_user_view(self):
        response = self.client.get('/catalog/mybook/',follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybook/")

    def test_my_book_list(self):
        self.client.login(username='John', password='secret')
        response = self.client.get('/catalog/mybook/',follow=True)
        self.assertEqual(str(response.context['user']),'John')
        self.assertEqual(len(response.context['book_instances']),15)

class MarkFormViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username='test_user',password='secret')
        test_user.save()
        self.client = Client()
        test_author = Author.objects.create(first_name='test', last_name='author')
        test_genre = Genre.objects.create(name='fiction')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='test_book', author=test_author, imprint='version-2020', isbn='isbn',language=test_language)
        test_book.genre.add(test_genre)
        test_bookinstance = BookInstance(due_back=date.today()-timedelta(days=1),status='o',borrower=test_user)
        test_bookinstance.save()
        self.id = BookInstance.objects.get().pk

    def test_anonymous_user_get_view(self):
        response = self.client.get(f'/catalog/{self.id}/suspend-due-back/')
        self.assertRedirects(response,f'/accounts/login/?next=/catalog/{self.id}/suspend-due-back/')

    def test_login_user_get_view(self):
        self.client.login(username='test_user',password='secret')
        response = self.client.get(f'/catalog/{self.id}/suspend-due-back/')
        self.assertEqual(response.status_code,403)

    def test_has_perms_user_get_view(self):
        permission = Permission.objects.get(codename='mark_bookinstance')
        user = User.objects.get()
        user.user_permissions.add(permission)
        self.client.login(username='test_user',password='secret')
        response = self.client.get(f'/catalog/{self.id}/suspend-due-back/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'mark_form.html')
        self.assertTrue('form' in response.context)

    def test_view_404(self):
        permission = Permission.objects.get(codename='mark_bookinstance')
        user = User.objects.get()
        user.user_permissions.add(permission)
        self.client.login(username='test_user',password='secret')
        id = uuid.uuid4()
        response = self.client.get(f'/catalog/{id}/suspend-due-back/')
        self.assertEqual(response.status_code, 404)

    def test_post_view_past_date(self):
        permission = Permission.objects.get(codename='mark_bookinstance')
        user = User.objects.get()
        user.user_permissions.add(permission)
        self.client.login(username='test_user',password='secret')
        response = self.client.post(f'/catalog/{self.id}/suspend-due-back/',{'due_back':date.today()-timedelta(days=1)})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'mark_form.html')
        self.assertFormError(response,'form','due_back','The date must be between today and three weeks later.')

    def test_post_view_current_date(self):
        permission = Permission.objects.get(codename='mark_bookinstance')
        user = User.objects.get()
        user.user_permissions.add(permission)
        self.client.login(username='test_user',password='secret')
        response = self.client.post(f'/catalog/{self.id}/suspend-due-back/',{'due_back':date.today()+timedelta(days=3)})
        self.assertRedirects(response,'/catalog/manage-borrowed-books/')

    def test_post_view_future_date(self):
        permission = Permission.objects.get(codename='mark_bookinstance')
        user = User.objects.get()
        user.user_permissions.add(permission)
        self.client.login(username='test_user',password='secret')
        response = self.client.post(f'/catalog/{self.id}/suspend-due-back/',{'due_back':date.today()-timedelta(weeks=4)})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'mark_form.html')
        self.assertFormError(response,'form','due_back','The date must be between today and three weeks later.')