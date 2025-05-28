from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from app1.forms import ContactForm

def contact_section(request):
    success = False
    error = ""
    if request.method == "POST" and request.POST.get("contact_form_submitted"):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            full_message = _("Mensaje de: %(name)s <%(email)s>\n\n%(msg)s") % {
                "name": name, "email": email, "msg": message
            }

            try:
                send_mail(
                    subject=_("Contacto desde extracsol.com: %(subject)s") % {"subject": subject},
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["info@extracsol.com"],
                    fail_silently=False,
                )
                success = True
                form = ContactForm()
            except Exception:
                error = _("No se pudo enviar el mensaje. Intenta de nuevo más tarde.")
        else:
            error = _("Por favor completa todos los campos correctamente.")
    else:
        form = ContactForm()

    return form, success, error