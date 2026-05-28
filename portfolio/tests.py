from django.test import TestCase
from django.urls import reverse

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


class ProjectListViewTests(TestCase):
    def test_sample_data_used_when_no_projects(self):
        response = self.client.get(reverse('portfolio:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['using_sample_data'])
        self.assertContains(response, 'TropicTrack POS and Inventory')

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
        self.assertNotContains(response, 'TropicTrack POS and Inventory')
