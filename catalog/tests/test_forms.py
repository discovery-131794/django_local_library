from django.test import TestCase
from catalog.forms import MarkForm
from catalog.models import BookInstance
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class MarkFormTest(TestCase):

    def test_id(self):
        form = MarkForm()
        self.assertTrue(form.fields['id'].disabled==True)

    def test_due_back(self):
        form = MarkForm()
        self.assertEqual(form.fields['due_back'].label, 'Renew_due_back')

    def test_save(self):
        BookInstance.objects.create(id='220e0e58fd564ef98c1a34612472e16a', due_back='2020-03-25', status='o')
        form = MarkForm(data={'due_back': '2020-04-25'})
        form.save('220e0e58fd564ef98c1a34612472e16a')
        self.assertEqual(BookInstance.objects.get(id='220e0e58fd564ef98c1a34612472e16a').due_back.isoformat(),'2020-04-25')

    def test_clean_due_back_past(self):
        form = MarkForm(data={'due_back': str(date.today()-timedelta(days=1))},initial={'id': '220e0e58fd564ef98c1a34612472e16a'})
        self.assertFalse(form.is_valid())

    def test_clean_due_back_current(self):
        form = MarkForm(data={'due_back': str(date.today()+timedelta(days=3))},initial={'id': '220e0e58fd564ef98c1a34612472e16a'})
        self.assertTrue(form.is_valid())

    def test_clean_due_back_future(self):
        form = MarkForm(data={'due_back': str(date.today()+timedelta(weeks=4))}, initial={'id': '220e0e58fd564ef98c1a34612472e16a'})
        self.assertFalse(form.is_valid())