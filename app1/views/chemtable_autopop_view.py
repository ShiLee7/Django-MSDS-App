from django.http import JsonResponse
from django.views.decorators.http import require_GET
from app1.utils import *

@require_GET
def chemtable_autopopulate(request):
    cas_number = request.GET.get('cas_number')
    if not cas_number:
        return JsonResponse({'error': 'CAS number not provided.'}, status=400)
    
    cid = get_cid_from_cas(cas_number)
    if cid is None:
        return JsonResponse({'error': 'No compound found for the provided CAS number.'}, status=404)
    
    # Use the provided utility functions to get the values
    data = {
        'chemical_name': get_synonyms_from_cas(cas_number)[0],
        'molecular_formula': get_mol_for(cid),
        'boiling_point': get_boil(cid),
        't_change': get_melt(cid),  # Melting point is used for t_change
        'phys': get_phys(cid),
        'solubility': get_solu(cid),
        'acute_toxicity_estimates': get_immi_eff(cid),
    }
    return JsonResponse(data)