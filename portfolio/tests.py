from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project
from .sample_data import SAMPLE_PROJECTS
from .views import _prepare_story, _split_benefit


# Prod settings have SECURE_SSL_REDIRECT=True, which the test client
# follows as a 301 before the view ever runs. Suppressing it here is the
# standard fix and doesn't change production behaviour.
BASE_OVERRIDES = dict(SECURE_SSL_REDIRECT=False, SECURE_HSTS_SECONDS=0)

# prod.py uses CompressedManifestStaticFilesStorage, which requires a
# pre-built staticfiles manifest (created by collectstatic in Step 6 of
# the deploy script). Tests run in Step 5, so the manifest may be stale
# or missing entries for newly added files, causing static() to raise
# ValueError even though the file physically exists in STATICFILES_DIRS.
# Overriding to the plain storage makes static() return a direct URL
# without needing the manifest, giving correct results in tests without
# changing production behaviour at all.
STATIC_OVERRIDES = dict(
    **BASE_OVERRIDES,
    STORAGES={
        'default':     {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)


class ProjectModelTests(TestCase):
    def test_slug_autopopulates_from_title(self):
        project = Project.objects.create(
            title='TropicTrack POS and Inventory',
            client_type='Food and Beverage',
            description='A test project.',
        )
        self.assertEqual(project.slug, 'tropictrack-pos-and-inventory')

    def test_cover_image_none_when_no_images(self):
        project = Project.objects.create(
            title='Empty Project',
            client_type='Test',
            description='No images yet.',
        )
        self.assertIsNone(project.cover_image)


@override_settings(**BASE_OVERRIDES)
class ProjectListViewTests(TestCase):
    def test_sample_data_used_when_no_projects(self):
        response = self.client.get(reverse('portfolio:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['using_sample_data'])
        self.assertContains(response, 'Forging a System That Scales')

    def test_hero_shows_description_under_the_tagline(self):
        response = self.client.get(reverse('portfolio:list'))
        # Fragment without apostrophes (the template HTML-escapes them).
        self.assertContains(response, 'Custom gates, fences, window bars')

    def test_real_projects_used_when_published(self):
        Project.objects.create(
            title='Live Project',
            client_type='Test',
            description='A real project.',
            tech_stack=['Python'],
            highlights=['Highlight one'],
            is_published=True,
        )
        response = self.client.get(reverse('portfolio:list'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['using_sample_data'])
        self.assertContains(response, 'Live Project')
        self.assertNotContains(response, 'Forging a System That Scales')


@override_settings(**STATIC_OVERRIDES)
class StoryPreparationTests(TestCase):
    def test_split_benefit_separates_lead_phrase(self):
        self.assertEqual(
            _split_benefit('Quotes in Minutes: The system handles it.'),
            {'lead': 'Quotes in Minutes', 'text': 'The system handles it.'},
        )

    def test_split_benefit_without_lead_keeps_whole_text(self):
        self.assertEqual(
            _split_benefit('Just a plain sentence.'),
            {'lead': '', 'text': 'Just a plain sentence.'},
        )

    def test_split_benefit_ignores_colon_in_a_long_sentence(self):
        long_sentence = 'x' * 80 + ': and then some more text'
        self.assertEqual(_split_benefit(long_sentence)['lead'], '')

    def test_story_images_found_from_prefix(self):
        story = _prepare_story({
            'title': "Thompson's Steel Fabricators Ltd",
            'image_prefix': 'Thompson_s_Steel_Fabricators_OS',
            'benefits': [],
        })
        self.assertEqual(story['slug'], 'thompsons-steel-fabricators-ltd')
        self.assertTrue(story['splash_url'].endswith('Thompson_s_Steel_Fabricators_OS-Splash.jpg'))
        self.assertGreater(len(story['screenshots']), 0)
        self.assertTrue(story['screenshots'][0].endswith('Thompson_s_Steel_Fabricators_OS-1.jpg'))

    def test_story_with_no_images_degrades_gracefully(self):
        story = _prepare_story({'title': 'No Pictures', 'image_prefix': 'does_not_exist'})
        self.assertIsNone(story['splash_url'])
        self.assertEqual(story['screenshots'], [])

    def test_every_sample_story_resolves_its_images(self):
        """Catches a typo'd image_prefix (or a missing/misnamed file) in sample_data.py."""
        for raw in SAMPLE_PROJECTS:
            with self.subTest(story=raw['title']):
                story = _prepare_story(raw)
                self.assertIsNotNone(
                    story['splash_url'],
                    f"No {raw['image_prefix']}-Splash.jpg found in static/images/clientstories/",
                )
                self.assertGreater(
                    len(story['screenshots']), 0,
                    f"No {raw['image_prefix']}-1.jpg found in static/images/clientstories/",
                )

    def test_every_sample_story_has_a_description(self):
        for raw in SAMPLE_PROJECTS:
            with self.subTest(story=raw['title']):
                self.assertTrue(raw.get('description', '').strip())
