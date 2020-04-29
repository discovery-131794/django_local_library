from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from . import models
import json
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import MarkForm, CreateAuthorModelForm, UpdateAuthorModelForm
from django.views.generic.edit import FormView, BaseCreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin

# Create your views here.
def index(request):
    book_num = models.Book.objects.count()
    bookinstance_num = models.BookInstance.objects.count()
    a_bookinstance_num = models.BookInstance.objects.filter(status='a').count()
    author_num = models.Author.objects.count()
    visit_num = request.session.get('visit_num', 0)
    request.session['visit_num']  = visit_num + 1
    context = {
        'book_num': book_num,
        'bookinstance_num': bookinstance_num,
        'a_bookinstance_num': a_bookinstance_num,
        'author_num': author_num,
        'visit_num': request.session['visit_num']
    }
    return render(request, 'index.html', context)

def update(request):
    #data = serializers.serialize('json', models.EmailAddress.objects.all())
    #record = serializers.deserialize('json', request.body)
    #record.object.save()
    #data = request.POST
    #Deserializer(data)
    #data = json.load(data)
    #Deserializer(data)
    data = json.loads(request.body)
    #record = models.EmailAddress(userid=request.POST.get('pk'), address=request.POST.get('address'), role=request.POST.get('role'))
    record = models.Email(userid=data.get('pk'), address=data.get('address'), role=data.get('role'))
    record.save()
    return JsonResponse({'success': ''})

def delete(request):
    data = json.loads(request.body)
    if(not data.get('address')):
        return JsonResponse({'message':'请输入邮箱地址'})
    else:
        models.Email.objects.filter(address=data.get('address')).delete()
        return JsonResponse({'message': '成功删除该邮箱地址'})

class BooksView(ListView):
    model = models.Book
    #context_object_name = 'book_list'
    template_name = 'all_book.html'
    ordering = ['title']
    paginate_by = 2

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AuthorView(ListView):
    template_permissons_add = ('catalog.add_author',)
    model = models.Author
    template_name = 'all_author.html'
    ordering = ['first_name', 'last_name']
    paginate_by  = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update({'has_perms': self.request.user.has_perms(self.template_permissons_add)})
        return context

class BookDetailView(DetailView):
    model = models.Book
    #context_object_name = 'book'
    template_name = 'book_detail.html'

class AuthorDetailView(DetailView):
    template_permissons_change = ('catalog.change_author',)
    template_permissons_delete = ('catalog.delete_author',)
    model = models.Author
    template_name = 'author_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update({'has_perms_change': self.request.user.has_perms(self.template_permissons_change)})
        context.update({'has_perms_delete': self.request.user.has_perms(self.template_permissons_delete)})
        return context

@login_required
def mybook(request):
    user = request.user
    book_instances = models.BookInstance.objects.filter(borrower=user.pk)
    context = {'book_instances': book_instances}
    return render(request, 'mybook.html', context)

def manage_borrowed_books(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            book_instances = models.BookInstance.objects.filter(status='o')
            context = {'book_instances': book_instances}
            if request.user.has_perms(('catalog.mark_bookinstance',)):
                context.update({'can_mark': True})
            return render(request, 'manage-borrowed-books.html', context)
        else:
            return HttpResponse('You don\'t have permission to view this page.')
    else:
        return HttpResponse('Please login to access this page.')

class MarkFormView(PermissionRequiredMixin, FormView):
    permission_required = 'catalog.mark_bookinstance'
    success_url = reverse_lazy('manage-borrowed-books')
    form_class = MarkForm
    template_name = 'mark_form.html'
    #title = 'Suspend Due Back'

    """
    def get_context_data(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = self.kwargs['id']
        return super().get_context_data(**kwargs)
    """

    def get_initial(self):
        self.initial = {'id': self.kwargs['id']}
        return super().get_initial()

    def form_valid(self, form):
        id = self.kwargs['id']
        form.save(id)
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(models.BookInstance, pk=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

class CreateAuthorModelFormView(PermissionRequiredMixin, TemplateResponseMixin, BaseCreateView):
    permission_required = ('catalog.add_author', )
    success_url = reverse_lazy('show-authors')
    template_name = 'create_author.html'
    form_class = CreateAuthorModelForm


class UpdateAuthorModelFormView(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.change_author',)
    template_name = 'update_author.html'
    form_class = UpdateAuthorModelForm
    template_name_suffix = None
    model = models.Author

class DeleteAuthorView(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.delete_author',)
    template_name = 'delete_author.html'
    template_name_suffix = None
    model = models.Author
    success_url = reverse_lazy('show-authors')

    
        




        