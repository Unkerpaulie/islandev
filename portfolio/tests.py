from django.test import TestCase

from .models import Project


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
