from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    i18n = True  # enables alternate hreflang for all LANGUAGES
    languages = [lang_code for lang_code, _ in settings.LANGUAGES]

    def items(self):
        return [
            'home',
            'iq',
            'edu',
            'msds_create',
            'about',
            'maintenance',
            'chemtable_create',
            'regulatory',
            # you can include 'ads-txt' if you want but usually not needed
            # dynamic pages like PDFs or success pages are usually not indexed
            # since they are not real content pages
        ]

    def location(self, item):
        return reverse(item)