from django.forms.forms import Form
from django.forms.models import ModelForm
from django.forms.fields import CharField, DateField
from .models import BookInstance
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from .models import Author

class MarkForm(Form):
    id = CharField(label='ID', disabled=True)
    due_back = DateField(label='Renew_due_back', help_text='Input date between today and three weeks later.')

    def save(self, id):
        bookinstance = BookInstance.objects.get(id=id)
        bookinstance.due_back = self.data['due_back']
        bookinstance.save()

    def clean_due_back(self):
        due_back = self.cleaned_data['due_back']
        if date.fromisoformat(self.data['due_back']) < date.today() or date.fromisoformat(self.data['due_back']) > (date.today()+timedelta(days=21)):
            raise ValidationError('The date must be between today and three weeks later.')
        return due_back

class CreateAuthorModelForm(ModelForm):
    class Meta:
        model = Author
        fields = '__all__'

class UpdateAuthorModelForm(ModelForm):
    class Meta:
        model = Author
        fields = '__all__'