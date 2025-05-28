from django.urls import path
from django.conf.urls.i18n import set_language
from django.views.generic import TemplateView
from .views import home, iq, MSDSWizard, generate_msds_pdf, edu, about, maintenance
from .views.sds_wizard_view import FORMS
from .views.create_chemtable import ChemTableCreateView
from .views.chemtable_autopop_view import chemtable_autopopulate
from .views.chemtable_pdf_view import generate_chemtable_pdf


urlpatterns = [
    path("", home, name="home"),
    path("iq", iq, name="iq"),
    path("edu", edu, name="edu"),
    path("msds/create", MSDSWizard.as_view(FORMS), name="msds_create"),
    path("msds/<int:msds_id>/pdf/", generate_msds_pdf, name="generate_msds_pdf"),
    path('about', about, name='about'),
    path('maintenance', maintenance, name='maintenance'),
    path('i18n/set_language/', set_language, name='set_language'),
	path('chemtable/', ChemTableCreateView.as_view(), name='chemtable_create'),
	path('chemtable/autopopulate/', chemtable_autopopulate, name='chemtable_autopopulate'),
	path('chemtable/success/<int:chemtable_id>/', TemplateView.as_view(template_name='chemtable_success.html'), name='chemtable_success'),
	path("chemtable/<int:chemtable_id>/pdf/", generate_chemtable_pdf, name="generate_chemtable_pdf"),
]