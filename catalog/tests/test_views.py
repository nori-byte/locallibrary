from datetime import datetime

from django.test import TestCase
from django.shortcuts import render, get_object_or_404
from django.views import generic

from catalog.forms import RenewBookForm
# Create your tests here.

from catalog.models import Author, BookInstance, Genre, Book
from django.urls import reverse

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 3)

from django.contrib.auth.mixins import LoginRequiredMixin


class Language:
    pass


class HttpResponseRedirect:
    pass


def permission_required(param):
    pass


class Permission:
    pass


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Обобщённый класс отображения списка взятых книг текущим пользователем
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


    @permission_required('catalog.can_mark_returned')
    def renew_book_librarian(request, pk):
        """
        Функция отображения обновления экземпляра BookInstance библиотекарем
        """
        book_inst = get_object_or_404(BookInstance, pk=pk)

        # Если это POST-запрос, тогда обработать данные формы
        if request.method == 'POST':

            # Создать объект формы и заполнить её данными из запроса (связывание/биндинг):
            form = RenewBookForm(request.POST)

            # Проверка валидности формы:
            if form.is_valid():
                # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
                book_inst.due_back = form.cleaned_data['renewal_date']
                book_inst.save()

                # переход по URL-адресу:
                return HttpResponseRedirect(reverse('all-borrowed'))

        # Если это GET-запрос (или что-то ещё), то создаём форму по умолчанию
        else:
            proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
            form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

        return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

    from django.contrib.auth.models import \
        Permission  # Required to grant the permission needed to set a book as returned.

    class RenewBookInstancesViewTest(TestCase):

        def setUp(self, User=None):
            # Создание пользователя
            test_user1 = User.objects.create_user(username='testuser1', password='12345')
            test_user1.save()

            test_user2 = User.objects.create_user(username='testuser2', password='12345')
            test_user2.save()
            permission = Permission.objects.get(name='Set book as returned')
            test_user2.user_permissions.add(permission)
            test_user2.save()

            # Создание книги
            test_author = Author.objects.create(first_name='John', last_name='Smith')
            test_genre = Genre.objects.create(name='Fantasy')
            test_language = Language.objects.create(name='English')
            test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
                                            author=test_author, language=test_language, )
            # Создание жанра Create genre as a post-step
            genre_objects_for_book = Genre.objects.all()
            test_book.genre = genre_objects_for_book
            test_book.save()

            # Создание объекта BookInstance для для пользователя test_user1
            return_date = datetime.date.today() + datetime.timedelta(days=5)
            self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                                  due_back=return_date, borrower=test_user1, status='o')

            # Создание объекта BookInstance для для пользователя test_user2
            return_date = datetime.date.today() + datetime.timedelta(days=5)
            self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                                  due_back=return_date, borrower=test_user2, status='o')

