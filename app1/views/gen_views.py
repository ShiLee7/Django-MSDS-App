from django.shortcuts import render
from .contact_view import contact_section

def home(request):
    form, success, error = contact_section(request)
    return render(request, 'home.html', {
        "form": form, "success": success, "error": error, "show_contact": True
    })

def iq(request):
    form, success, error = contact_section(request)
    return render(request, 'iq.html', {
        "form": form, "success": success, "error": error, "show_contact": True
    })

def edu(request):
    form, success, error = contact_section(request)
    return render(request, 'edu.html', {
        "form": form, "success": success, "error": error, "show_contact": True
    })

def about(request):
    form, success, error = contact_section(request)
    return render(request, 'about.html', {
        "form": form, "success": success, "error": error, "show_contact": True
    })

def maintenance(request):
    # Aquí podrías no mostrar el contacto (por ejemplo: "show_contact": False)
    return render(request, 'maintenance.html', {
        "show_contact": False
    })
