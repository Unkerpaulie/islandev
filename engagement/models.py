from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """A newsletter subscriber from the homepage newsletter block."""

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.name} <{self.email}>'

    # BookingRequest and ContactInquiry have been removed from this project.
    # Those responsibilities now live in the agents system (agents.islan.dev).
    # The database tables for those models still exist on the server but are
    # no longer used; they can be dropped once the transition is confirmed.
