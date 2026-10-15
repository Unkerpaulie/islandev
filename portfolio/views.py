import json

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.text import slugify
from django.views.generic import DetailView, ListView

from .models import Project
from .sample_data import SAMPLE_PROJECTS

# Where story images live under static/, and their format. A story's images are
# located from its `image_prefix`: {prefix}-Splash.jpg and {prefix}-1.jpg, -2.jpg, ...
STORY_IMAGE_DIR = 'images/clientstories'
STORY_IMAGE_EXT = 'jpg'

# A benefit's "lead phrase" is the text before the first ': '. Anything longer
# than this is probably a sentence that happens to contain a colon, not a headline.
MAX_BENEFIT_LEAD_LENGTH = 70


def _story_image_url(filename):
    """Return the static URL for a story image, or None if it isn't there.

    Existence is checked with the staticfiles *finders* (the source static
    dirs), which behaves the same in dev and prod. In prod the manifest storage
    raises ValueError for a file it has not collected yet; treating that as
    "missing" means a freshly added image can never 500 the page.
    """
    path = f'{STORY_IMAGE_DIR}/{filename}'
    if not finders.find(path):
        return None
    try:
        return static(path)
    except ValueError:
        return None


def _find_screenshots(prefix):
    """Collect {prefix}-1.jpg, {prefix}-2.jpg, ... until the first missing number."""
    urls = []
    number = 1
    while True:
        url = _story_image_url(f'{prefix}-{number}.{STORY_IMAGE_EXT}')
        if not url:
            return urls
        urls.append(url)
        number += 1


def _split_benefit(text):
    """Split 'Lead phrase: explanation' into {'lead', 'text'} for the template."""
    lead, separator, rest = text.partition(': ')
    if separator and len(lead) <= MAX_BENEFIT_LEAD_LENGTH:
        return {'lead': lead, 'text': rest}
    return {'lead': '', 'text': text}


def _prepare_story(raw):
    """Turn a SAMPLE_PROJECTS entry into what the template renders.

    The entry itself stays pure content (see sample_data.py). Everything
    derived from it (anchor slug, image URLs, benefit headlines) is added here.
    """
    story = dict(raw)
    prefix = raw.get('image_prefix', '')
    story['slug'] = slugify(raw['title'])
    story['splash_url'] = (
        _story_image_url(f'{prefix}-Splash.{STORY_IMAGE_EXT}') if prefix else None
    )
    story['screenshots'] = _find_screenshots(prefix) if prefix else []
    # Handed to the Alpine screenshot viewer as a JS array; the template's
    # autoescaping makes it safe inside an HTML attribute.
    story['screenshots_json'] = json.dumps(story['screenshots'])
    story['benefits'] = [_split_benefit(b) for b in raw.get('benefits', [])]
    return story


def _project_to_view_model(project):
    """Flatten a Project (and its images) into the dict shape the template expects.

    The template iterates `projects` as a uniform list of dicts so it doesn't
    care whether the data came from the database or the sample fallback.

    NOTE: the Project model has not been migrated to the story schema yet
    (no problem / solution / benefits / image_prefix), so database-backed
    projects only populate the fields that exist on the model.
    """
    return {
        'title': project.title,
        'slug': project.slug,
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
            ctx['projects'] = [_prepare_story(s) for s in SAMPLE_PROJECTS]
            ctx['using_sample_data'] = True
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related('images')
