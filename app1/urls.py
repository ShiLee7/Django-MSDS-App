from django.urls import path
from django.conf.urls.i18n import set_language
from .views import home, iq, MSDSWizard, generate_msds_pdf, edu, fintech, about, maintenance
from .views.sds_wizard_view import FORMS

urlpatterns = [
    path("", home, name="home"),
    path("iq", iq, name="iq"),
    path("edu", edu, name="edu"),
    path("fintech", fintech, name="fintech"),
    path("msds/create", MSDSWizard.as_view(FORMS), name="msds_create"),
    path("msds/<int:msds_id>/pdf/", generate_msds_pdf, name="generate_msds_pdf"),
    path('about', about, name='about'),
    path('maintenance', maintenance, name='maintenance'),
    path('i18n/set_language/', set_language, name='set_language')
]