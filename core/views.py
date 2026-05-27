from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'


class ServicesView(TemplateView):
    template_name = 'core/services.html'
