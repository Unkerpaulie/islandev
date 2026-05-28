from django.views.generic import TemplateView

from . import home_content


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['services'] = home_content.SERVICES
        ctx['reasons'] = home_content.REASONS
        ctx['featured_projects'] = home_content.FEATURED_PROJECTS
        ctx.setdefault('subscriber_form', None)
        return ctx


class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['services'] = home_content.SERVICES
        return ctx
