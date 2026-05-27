from django.views.generic import TemplateView


class BookView(TemplateView):
    template_name = 'engagement/book.html'


class ContactView(TemplateView):
    template_name = 'engagement/contact.html'
