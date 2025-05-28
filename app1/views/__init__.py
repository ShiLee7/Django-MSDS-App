from .gen_views import home, iq, edu, about, maintenance
from .sds_wizard_view import MSDSWizard
from .sds_pdf_view import generate_msds_pdf
from .chemtable_pdf_view import generate_chemtable_pdf

__all__ = ["home", "iq", "MSDSWizard", "generate_msds_pdf", "edu", "about", 'maintenance', "generate_chemtable_pdf"]