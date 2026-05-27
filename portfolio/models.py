from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Project(models.Model):
    """A portfolio entry — a system built for a real client."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    client_type = models.CharField(
        max_length=120,
        help_text="Industry or sector label (e.g. 'Food and Beverage').",
    )
    tech_stack = models.JSONField(
        default=list,
        blank=True,
        help_text="List of technology labels, e.g. ['React', 'Node.js', 'PostgreSQL'].",
    )
    description = models.TextField()
    highlights = models.JSONField(
        default=list,
        blank=True,
        help_text="List of short bullet points describing key capabilities.",
    )

    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(
        default=False,
        help_text="Show on the homepage portfolio teaser section.",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:detail', kwargs={'slug': self.slug})

    @property
    def cover_image(self):
        return self.images.order_by('display_order', 'id').first()


class ProjectImage(models.Model):
    """A screenshot belonging to a project. Displayed in a per-project carousel."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='portfolio/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return f'{self.project.title} — image #{self.pk}'
