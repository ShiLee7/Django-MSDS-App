from django.shortcuts import render, redirect, get_object_or_404
from app1.forms import *
from app1.models import *
from app1.constants import *
from formtools.wizard.views import SessionWizardView
from app1.utils import *
from django.utils.html import escapejs
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame, PageTemplate, Flowable, Image as RLImage, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders
from io import BytesIO
from django.http import HttpResponse

import datetime
import json
import logging
import requests
import cairosvg

logger = logging.getLogger(__name__)

form_classes = [
    MSDSSection1Form,
    MSDSSection2Form,
    MSDSSection3Form,
    MSDSSection4Form,
    MSDSSection5Form,
    MSDSSection6Form,
    MSDSSection7Form,
    MSDSSection8Form,
    MSDSSection9Form,
    MSDSSection10Form,
    MSDSSection11Form,
    MSDSSection12Form,
    MSDSSection13Form,
    MSDSSection14Form,
    MSDSSection15Form,
    MSDSSection16Form,
]

FORMS = [(f'section{i+1}', form_class) for i, form_class in enumerate(form_classes)]
TEMPLATES = {f'section{i+1}': f'msds_section{i+1}.html' for i in range(len(form_classes))}

class MSDSWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        template_name = TEMPLATES[self.steps.current]
        logger.debug(f"Using template: {template_name} for step: {self.steps.current}")
        return [template_name]


    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        if step == 'section2':
            if 'section2_cached_data' in self.storage.data:
                cached_data = self.storage.data['section2_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas_number = data.get('cas_number')
                if cas_number:
                    cached_data = {}
                    cid = get_cid_from_cas(cas_number)
                    if cid:
                        classification = get_classification_from_cid(cid)
                        if classification:
                            cached_data['classification'] = classification

                        signal_word = get_signal_word(cid)
                        if signal_word:
                            cached_data['signal_word'] = signal_word
                        else:
                            logger.warning(f"No signal word found for CID {cid}")

                        h_codes = get_h_codes(cid)
                        if h_codes:
                            cached_data['hazard_statements'] = '; '.join(h_codes)

                        p_codes = get_p_codes(cid)
                        if p_codes:
                            for category, codes_dict in p_codes.items():
                                statements = [f"{code}: {desc}" for code, desc in codes_dict.items()]
                                cached_data[f'{category}_precautionary_statements'] = '; '.join(statements)

                        svg_data = fetch_and_find_svg_urls(cid)
                        if svg_data:
                            cached_data['label_elements'] = svg_data
                            existing_labels = [elem['description'] for elem in svg_data]
                            predefined_labels = PICTOGRAMS.keys()
                            cached_data['additional_pictograms'] = list(set(existing_labels) & set(predefined_labels))
                        else:
                            logger.warning(f"No SVG data found for CID {cid}")

                    self.storage.data['section2_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section3':
            if 'section3_cached_data' in self.storage.data:
                cached_data = self.storage.data['section3_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas_number = data.get('cas_number')

                cached_data = {}

                try:
                    iupac_name = get_iupac(cas_number)
                    if iupac_name != '':
                        cached_data['chemical_name'] = iupac_name
                    else:
                        logger.warning(f"No IUPAC name found for CAS {cas_number}")
                        cached_data['chemical_name'] = ''
                except Exception as e:
                    logger.error(f"Error fetching IUPAC name for CAS {cas_number}: {e}")
                    cached_data['chemical_name'] = ''

                try:
                    synonyms = get_synonyms_from_cas(cas_number)
                    if synonyms:
                        cached_data['synonyms'] = sorted(synonyms, key=lambda x: x.lower())
                        
                except Exception as e:
                    logger.error(f"Error fetching synonyms for CAS {cas_number}: {e}")
                    cached_data['synonyms'] = []

                self.storage.data['section3_cached_data'] = cached_data
                initial.update(cached_data)

        if step == 'section4':
            if 'section4_cached_data' in self.storage.data:
                cached_data = self.storage.data['section4_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        first_aid = get_first_aid(cid)

                        if first_aid != []:

                            cached_data['aid_inhal'] = first_aid[0]
                            cached_data['aid_inges'] = first_aid[3]
                            cached_data['aid_eye'] = first_aid[2]
                            cached_data['aid_skin'] = first_aid[1]

                    except Exception as e:
                        logger.error(f"Error fetching First Aid data for CAS {cas}: {e}")
                        cached_data['aid_inhal'] = ''
                        cached_data['aid_inges'] = ''
                        cached_data['aid_eye'] = ''
                        cached_data['aid_skin'] = ''

                    self.storage.data['section4_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section5':
            if 'section5_cached_data' in self.storage.data:
                cached_data = self.storage.data['section5_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        fire = get_fire(cid)

                        if fire != []:

                            cached_data['suitable_extinguishing_media'] = fire[0]
                            cached_data['special_protective_actions'] = fire[1]

                    except Exception as e:
                        logger.error(f"Error fetching Fire Protection data for CAS {cas}: {e}")
                        cached_data['suitable_extinguishing_media'] = ''
                        cached_data['special_protective_actions'] = ''

                    self.storage.data['section5_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section6':
            if 'section6_cached_data' in self.storage.data:
                cached_data = self.storage.data['section6_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        acci = get_acci(cid)
                        if acci != []:

                            cached_data['personal_precautions'] = str(acci)

                    except Exception as e:
                        logger.error(f"Error fetching Accidental Release Measures' data for CAS {cas}: {e}")
                        cached_data['personal_precautions'] = ''

                    self.storage.data['section6_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section7':
            if 'section7_cached_data' in self.storage.data:
                cached_data = self.storage.data['section7_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        hand_stor = get_hand_stor(cid)
                        safe_stor = get_safe_stor(cid)

                        if hand_stor != []:

                            cached_data['precautions_for_safe_handling'] = str(hand_stor)

                        if safe_stor != '':

                            cached_data['conditions_for_safe_storage'] = safe_stor

                    except Exception as e:
                        logger.error(f"Error fetching Handling and Storage data for CAS {cas}: {e}")
                        cached_data['precautions_for_safe_handling'] = ''
                        cached_data['conditions_for_safe_storage'] = ''

                    self.storage.data['section7_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section8':
            if 'section8_cached_data' in self.storage.data:
                cached_data = self.storage.data['section8_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        oel = get_oel(cid)
                        

                        if oel != []:

                            cached_data['control_parameters'] = 'Occupational Exposure Limits (OEL)\n' + oel.replace(';', '\n')

                    except Exception as e:
                        logger.error(f"Error fetching OEL data for CAS {cas}: {e}")
                        cached_data['control_parameters'] = ''

                    self.storage.data['section8_cached_data'] = cached_data
                    initial.update(cached_data)

        if step == 'section9':
            if 'section9_cached_data' in self.storage.data:
                cached_data = self.storage.data['section9_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:

                    try:
                        phys = get_phys(cid)
                        odor = get_odor(cid)
                        t_change = get_melt(cid)
                        boil = get_boil(cid)
                        flame = get_flame(cid)
                        flash = get_flash(cid)
                        autoig = get_autoig(cid)
                        pH = get_pH(cid)
                        solu = get_solu(cid)
                        vap_p = get_vap_p(cid)
                        vap_d = get_vap_d(cid)
                        

                        if phys != []:

                            cached_data['phys'] = str(phys)

                        if odor != []:
                            cached_data['odor'] = str(odor)

                        if t_change != []:
                            cached_data['t_change'] = str(t_change)

                        if boil != []:
                            cached_data['boiling_point'] = str(boil)

                        if flame != []:
                            cached_data['flammability_information'] = str(flame)

                        if flash != []:
                            cached_data['flash_point'] = str(flash)

                        if autoig != []:
                            cached_data['auto_ignition_temperature'] = str(autoig)

                        if pH != []:
                            cached_data['pH'] = str(pH)

                        if solu != []:
                            cached_data['solubility'] = str(solu)

                        if vap_p != []:
                            cached_data['vapor_pressure'] = str(vap_p)

                        if vap_d != []:
                            cached_data['relative_vapour_density'] = str(vap_d)

                    except Exception as e:
                        # Log the error with detailed context
                        logger.error(f"Error fetching section 9 data for CAS {cas}: {e}")
                        # Optionally add meaningful fallback data to indicate a failure
                        cached_data.update({
                            'phys': 'Data not available',
                            'odor': 'Data not available',
                            't_change': 'Data not available',
                            'boiling_point': 'Data not available',
                            'flammability_information': 'Data not available',
                            'flash_point': 'Data not available',
                            'auto_ignition_temperature': 'Data not available',
                            'pH': 'Data not available',
                            'solubility': 'Data not available',
                            'vapor_pressure': 'Data not available',
                            'relative_vapour_density': 'Data not available',
                        })

                self.storage.data['section9_cached_data'] = cached_data
                initial.update(cached_data)

        if step == 'section10':
            if 'section10_cached_data' in self.storage.data:
                cached_data = self.storage.data['section10_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:
                    try:
                        # Fetch data
                        reac = get_reac(cid)
                        h_reac = get_h_reac(cid)
                        h_decomp = get_h_decomp(cid)

                        # Populate cached data
                        if reac:
                            cached_data['reactivity'] = str(reac)
                        if h_reac:
                            cached_data['possibility_of_hazardous_reactions'] = str(h_reac)
                        if h_decomp:
                            cached_data['hazardous_decomposition_products'] = str(h_decomp)

                    except Exception as e:
                        # Log the error with detailed context
                        logger.error(f"Error fetching section 10 data for CAS {cas}: {e}")

                # Save cached data in storage
                self.storage.data['section10_cached_data'] = cached_data
                initial.update(cached_data)

        if step == 'section11':
            if 'section11_cached_data' in self.storage.data:
                cached_data = self.storage.data['section11_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:
                    try:
                        # Fetch data
                        symp = irritants(cid)
                        tox_data = get_tox_data(cid)
                        immi_eff = get_immi_eff(cid)
                        ch_eff = get_ch_eff(cid)
                        
                        if symp:
                            cached_data['symptoms'] = str(symp)

                        if tox_data:
                            cached_data['acute_toxicity_estimates'] = str(tox_data)

                        if immi_eff:
                            cached_data['immediate_effects'] = str(immi_eff)
                        
                        if ch_eff:
                            cached_data['chronic_effects'] = str(ch_eff)

                    except Exception as e:
                        # Log the error with detailed context
                        logger.error(f"Error fetching section 11 data for CAS {cas}: {e}")
                        # Add meaningful fallback data for failed fetches

                # Save cached data in storage
                self.storage.data['section11_cached_data'] = cached_data
                initial.update(cached_data)

        if step == 'section12':
            if 'section12_cached_data' in self.storage.data:
                cached_data = self.storage.data['section12_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                
                if cid:
                    try:
                        # Fetch data
                        eco_tox = get_eco_tox(cid)
                        other_eco = get_other_eco(cid)
                        bio_accu = get_bio_accu(cid)
                        mob_soil = get_mob_soil(cid)
                        degra = get_degra(cid)
                        
                        if eco_tox:
                            cached_data['ecotoxicity'] = str(eco_tox)

                        if other_eco:
                            cached_data['other_adverse_effects'] = str(other_eco)

                        if bio_accu:
                            cached_data['bioaccumulative_potential'] = str(bio_accu)

                        if mob_soil:
                            cached_data['mobility_in_soil'] = str(mob_soil)

                        if degra:
                            cached_data['persistence_and_degradability'] = str(degra)

                    except Exception as e:
                        # Log the error with detailed context
                        logger.error(f"Error fetching section 12 data for CAS {cas}: {e}")    

                # Save cached data in storage
                self.storage.data['section12_cached_data'] = cached_data
                initial.update(cached_data)

        if step == 'section14':
            if 'section14_cached_data' in self.storage.data:
                cached_data = self.storage.data['section14_cached_data']
                initial.update(cached_data)
            else:
                data = self.get_cleaned_data_for_step('section1') or {}
                cas = data.get('cas_number')
                cached_data = {}
                cid = get_cid_from_cas(cas)
                if cid:
                    try:
                        # Fetch data
                        UN = get_un(cid)
                        ship_name = get_shipping_name(cid)
                        
                        if UN:
                            cached_data['UN_number'] = str(UN)

                        if ship_name:
                            cached_data['UN_proper_shipping_name'] = str(ship_name)

                    except Exception as e:
                        # Log the error with detailed context
                        logger.error(f"Error fetching section 14 data for CAS {cas}: {e}")    

                # Save cached data in storage
                self.storage.data['section14_cached_data'] = cached_data
                initial.update(cached_data)

        return initial

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'section2':
            cached_data = self.storage.data.get('section2_cached_data', {})
            context['label_elements_json'] = json.dumps(cached_data.get('label_elements', []))
            context['pictograms_dict'] = PICTOGRAMS
            context['pictograms_json'] = json.dumps(PICTOGRAMS)

            categories = ['general', 'prevention', 'response', 'storage', 'disposal']
            context['initial_precautionary_statements_json'] = json.dumps({
                category: cached_data.get(f'{category}_precautionary_statements', '') for category in categories
            })
            context['categories'] = categories

        if self.steps.current == 'section3':
            cached_data = self.storage.data.get('section3_cached_data', {})
            context['synonyms'] = cached_data.get('synonyms', [])
            sec1_data = self.get_cleaned_data_for_step('section1') or {}
            cas_number = sec1_data.get('cas_number')
            context['cas_number'] = sec1_data.get('cas_number')
            
            reach_no = sec1_data.get('reach_no')
            if reach_no:
                context['reach_no'] = sec1_data.get('reach_no')
            else:
                context['reach_no'] = ''

            index_number = sec1_data.get('index_number')
            if index_number:
                context['index_number'] = sec1_data.get('index_number')
            else:
                context['index_number'] = ''        

        if self.steps.current == 'section4':
            cached_data = self.storage.data.get('section4_cached_data', {})
            context['description_of_first_aid'] = cached_data.get('description_of_first_aid', [])

        if self.steps.current == 'section14':  # Adjusted for Section 14
            cached_data = self.storage.data.get('section14_cached_data', {})
            context['un_pictograms_dict'] = DESC_TO_IMAGE_UN

        return context

    def process_step(self, form):
        # Log the QueryDict for the current step
        logger.debug(f"Step {self.steps.current} QueryDict: {self.request.POST}")
        
        # Log cleaned data for the current step if the form is valid
        if form.is_valid():
            logger.debug(f"Step {self.steps.current} cleaned_data: {form.cleaned_data}")
        else:
            logger.warning(f"Step {self.steps.current} has invalid data.")

        return super().process_step(form)

    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            logger.debug(f"Form {form.__class__.__name__} cleaned_data: {form.cleaned_data}")
            data.update(form.cleaned_data)

        additional_pictograms = data.pop('additional_pictograms', [])
        additional_label_elements = [{'url': PICTOGRAMS[label], 'description': label} for label in additional_pictograms]

        existing_label_elements = data.get('label_elements', [])
        combined_elements = existing_label_elements + additional_label_elements

        unique_elements = { (elem['url'], elem['description']): elem for elem in combined_elements }
        data['label_elements'] = list(unique_elements.values())

        try:
            msds_instance = MSDS.objects.create(**data)
            return render(self.request, 'done.html', {'msds': msds_instance})
        except Exception as e:
            logger.error(f"Error saving MSDS: {e}")
            return render(self.request, 'error.html', {'error': str(e)})

        form = super().get_form(step, data, files)
        if data and not form.is_valid():
            # Log any validation errors
            logger.debug(f"Validation errors in step {step}: {form.errors}")
        return form