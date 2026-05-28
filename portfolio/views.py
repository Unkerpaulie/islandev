from django.views.generic import DetailView, ListView

from .models import Project
from .sample_data import SAMPLE_PROJECTS


def _project_to_view_model(project):
    """Flatten a Project (and its images) into the dict shape the template expects.

    The template iterates `projects` as a uniform list of dicts so it doesn't
    care whether the data came from the database or the sample fallback.
    """
    return {
        'title': project.title,
        'client_type': project.client_type,
        'tech_stack': project.tech_stack or [],
        'description': project.description,
        'highlights': project.highlights or [],
        'image_urls': [img.image.url for img in project.images.all()],
    }


class ProjectListView(ListView):
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related('images')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = ctx['projects']
        if qs.exists():
            ctx['projects'] = [_project_to_view_model(p) for p in qs]
            ctx['using_sample_data'] = False
        else:
            ctx['projects'] = SAMPLE_PROJECTS
            ctx['using_sample_data'] = True
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related('images')
