from django.urls import reverse


def site(request):
    """Globals available in every template.

    `nav_links` is a list of (label, view_name, url) tuples used by the navbar
    partial for both the desktop and mobile menus. Keeping it here means the
    link list lives in one place and templates stay free of duplication.
    """
    nav_links = [
        ('Home', 'core:home', reverse('core:home')),
        ('Services', 'core:services', reverse('core:services')),
        ('Portfolio', 'portfolio:list', reverse('portfolio:list')),
        ('Contact', 'engagement:contact', reverse('engagement:contact')),
    ]
    return {
        'nav_links': nav_links,
    }
