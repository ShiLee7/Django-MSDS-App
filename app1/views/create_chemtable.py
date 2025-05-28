from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from app1.forms import *
from app1.models import *
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

class ChemTableCreateView(CreateView):
    model = ChemTable
    form_class = ChemTableForm
    template_name = 'chemtable.html'
    success_url = reverse_lazy('chemtable_success')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['chemical_formset'] = ChemicalFormSet(self.request.POST, prefix='chemical_set')
        else:
            data['chemical_formset'] = ChemicalFormSet(prefix='chemical_set')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        chemical_formset = context['chemical_formset']
        if chemical_formset.is_valid():
            self.object = form.save()
            chemical_formset.instance = self.object
            chemical_formset.save()
            return redirect('chemtable_success', chemtable_id=self.object.id)
        else:
            logger.error("Formset errors: %s", chemical_formset.errors)
            logger.error("Formset non_form_errors: %s", chemical_formset.non_form_errors())

            return self.render_to_response(self.get_context_data(form=form))