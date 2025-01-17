from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from .constants import *

class MSDSSection1Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'product_name',
            'product_number',
            'index_number',
            'reach_no',
            'cas_number',
            'manufacturer_name',
            'manufacturer_address',
            'phone_number',
            'emergency_phone',
            'recommended_use',
            'restrictions_on_use',
        ]
        error_messages = {
            'manufacturer_name': {
                'required': _("Por favor, ingrese el nombre del fabricante."),
                'max_length': _("El nombre del fabricante no puede exceder los 200 caracteres."),
            },
            'manufacturer_address': {
                'required': _("Por favor, ingrese la dirección del fabricante."),
            },
            'phone_number': {
                'required': _("Por favor, ingrese el número de teléfono."),
                'max_length': _("El número de teléfono no puede exceder los 50 caracteres."),
            },
            'emergency_phone': {
                'max_length': _("El número de teléfono de emergencia no puede exceder los 50 caracteres."),
            },
            'recommended_use': {
                'required': _("Por favor, ingrese el uso recomendado."),
                'max_length': _("El uso recomendado no puede exceder los 200 caracteres."),
            },
            'restrictions_on_use': {
                'max_length': _("Las restricciones de uso no pueden exceder los 200 caracteres."),
            },
        }
        widgets = {
            'cas_number': forms.TextInput(attrs={'size': 10, 'style': 'width: auto;'}),
            'index_number': forms.TextInput(attrs={'size': 10, 'style': 'width: auto;'}),
            'product_number': forms.TextInput(attrs={'size': 10, 'style': 'width: auto;'}),
            'product_name': forms.TextInput(attrs={'size': 40, 'style': 'width: auto;', 'placeholder': _("Nombre del producto")}),
            'manufacturer_name': forms.TextInput(attrs={'size': 40, 'style': 'width: auto;', 'placeholder': _("Nombre del fabricante")}),
            'reach_no': forms.TextInput(attrs={'size': 10, 'style': 'width: auto;'}),
            'manufacturer_address': forms.Textarea(attrs={'rows': 2, 'placeholder': _("Dirección del fabricante")}),
            'phone_number': forms.TextInput(attrs={'placeholder': _("+1-555-555-5555"), 'size': 20, 'style': 'width: auto;'}),
            'emergency_phone': forms.TextInput(attrs={'placeholder': _("+1-555-555-5555"), 'size': 20, 'style': 'width: auto;'}),
            'recommended_use': forms.TextInput(attrs={'placeholder': _("Uso previsto del producto")}),
            'restrictions_on_use': forms.TextInput(attrs={'placeholder': _("Restricciones de uso")}),
        }

class MSDSSection9Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'phys',  # Physical State/Appearance
            'colour',
            'odor',
            'pH',
            't_change',  # Melting Point/Freezing Point
            'boiling_point',  # Initial Boiling Point
            'flash_point',
            'evaporation_rate',
            'flammability_information',  # Flammability
            'vapor_pressure',
            'density',  # Density and/or relative density
            'relative_vapour_density',
            'solubility',
            'partition',  # Partition coefficient: n-octanol/water (log value)
            'auto_ignition_temperature',
            'decomposition_temperature',
            'kinematic_viscosity',  # Viscosity
            'particle_characteristics',  # Particle Characteristics
        ]

        widgets = {
            'phys': forms.Textarea(attrs={'style': 'width: auto;'}),
            'colour': forms.TextInput(attrs={'style': 'width: auto;'}),
            'odor': forms.TextInput(attrs={'style': 'width: auto;'}),
            'pH': forms.TextInput(attrs={'style': 'width: auto;'}),
            't_change': forms.TextInput(attrs={'style': 'width: auto;'}),
            'boiling_point': forms.TextInput(attrs={'style': 'width: auto;'}),
            'flash_point': forms.TextInput(attrs={'style': 'width: auto;'}),
            'evaporation_rate': forms.TextInput(attrs={'style': 'width: auto;'}),
            'flammability_information': forms.TextInput(attrs={'style': 'width: auto;'}),
            'vapor_pressure': forms.TextInput(attrs={'style': 'width: auto;'}),
            'density': forms.TextInput(attrs={'style': 'width: auto;'}),
            'relative_vapour_density': forms.TextInput(attrs={'style': 'width: auto;'}),
            'solubility': forms.TextInput(attrs={'style': 'width: auto;'}),
            'partition': forms.TextInput(attrs={'style': 'width: auto;'}),
            'auto_ignition_temperature': forms.TextInput(attrs={'style': 'width: auto;'}),
            'decomposition_temperature': forms.TextInput(attrs={'style': 'width: auto;'}),
            'kinematic_viscosity': forms.TextInput(attrs={'style': 'width: auto;'}),
            'particle_characteristics': forms.TextInput(attrs={'style': 'width: auto;'}),
        }


class MSDSSection2Form(forms.ModelForm):
    additional_pictograms = forms.MultipleChoiceField(
        choices=[(key, key) for key in PICTOGRAMS.keys()],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Agregar pictogramas adicionales')
    )
    
    class Meta:
        model = MSDS
        fields = [
            'classification',
            'label_elements',
            'signal_word',
            'hazard_statements',
            'general_statements',
            'prevention_statements',
            'response_statements',
            'storage_statements',
            'disposal_statements',
            'other_hazards'
        ]
        error_messages = {
            'classification': {
                'required': _("Por favor, ingrese la clasificación."),
            },
            'label_elements': {
                'required': _("Por favor, ingrese los elementos de etiqueta."),
            },
        }
        widgets = {
            'label_elements': forms.HiddenInput(),
            'other_hazards': forms.Textarea(attrs={'rows': 1, 'placeholder': _("Peligros no clasificados de otra manera (HNOC)")}),
            'classification': forms.Textarea(attrs={'style': 'width: auto;', 'placeholder': _("Clasificación del producto")})
        }

class MSDSSection3Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'substance_or_mixture',
            'chemical_name',
            'synonyms',
            'concentration',
            'other_unique_identifiers'
        ]
        error_messages = {
            'substance_or_mixture': {
                'required': _("Por favor, seleccione si es una sustancia o mezcla."),
            }
        }
        widgets = {
            'chemical_name': forms.TextInput(attrs={'placeholder': _("Nombre químico")}),
            'synonyms': forms.Textarea(attrs={'rows': 2, 'placeholder': _("Sinónimos")}),
            'concentration': forms.Textarea(attrs={'rows': 2, 'placeholder': _("Concentración")})
        }

class MSDSSection4Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'aid_inhal',
            'aid_inges',
            'aid_eye',
            'aid_skin',
            'symp_inhal',
            'symp_inges',
            'symp_eye',
            'symp_skin',
        ]
        widgets = {
    'aid_inhal': forms.Textarea(attrs={'rows': 2}),
    'aid_inges': forms.Textarea(attrs={'rows': 2}),
    'aid_eye': forms.Textarea(attrs={'rows': 2}),
    'aid_skin': forms.Textarea(attrs={'rows': 2}),
    'symp_inhal': forms.Textarea(attrs={'rows': 2}),
    'symp_inges': forms.Textarea(attrs={'rows': 2}),
    'symp_eye': forms.Textarea(attrs={'rows': 2}),
    'symp_skin': forms.Textarea(attrs={'rows': 2}),
        }


class MSDSSection5Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'suitable_extinguishing_media',
            'specific_hazards_arising',
            'special_protective_actions',
        ]
        widgets = {
            'suitable_extinguishing_media': forms.Textarea(attrs={'rows': 3}),
            'specific_hazards_arising': forms.Textarea(attrs={'rows': 3}),
            'special_protective_actions': forms.Textarea(attrs={'rows': 3}),
        }


class MSDSSection6Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'personal_precautions',
            'protective_equipment',
            'emergency_procedures',
            'environmental_precautions',
            'methods_and_materials_for_containment',
        ]
        widgets = {
            'personal_precautions': forms.Textarea(attrs={'rows': 3}),
            'protective_equipment': forms.Textarea(attrs={'rows': 3}),
            'emergency_procedures': forms.Textarea(attrs={'rows': 3}),
            'environmental_precautions': forms.Textarea(attrs={'rows': 3}),
            'methods_and_materials_for_containment': forms.Textarea(attrs={'rows': 3}),
        }

class MSDSSection7Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'precautions_for_safe_handling',
            'conditions_for_safe_storage',
        ]
        widgets = {
            'precautions_for_safe_handling': forms.Textarea(attrs={'rows': 3}),
            'conditions_for_safe_storage': forms.Textarea(attrs={'rows': 3}),
        }

class MSDSSection8Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'control_parameters',
            'appropriate_engineering_controls',
            'individual_protection_measures',
        ]
        widgets = {
            'control_parameters': forms.Textarea(attrs={'rows': 3}),
            'appropriate_engineering_controls': forms.Textarea(attrs={'rows': 3}),
            'individual_protection_measures': forms.Textarea(attrs={'rows': 3}),
        }


class MSDSSection10Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'reactivity',
            'chemical_stability',
            'possibility_of_hazardous_reactions',
            'conditions_to_avoid',
            'incompatible_materials',
            'hazardous_decomposition_products',
        ]
        widgets = {
            'reactivity': forms.Textarea(attrs={'rows': 3}),
            'chemical_stability': forms.Textarea(attrs={'rows': 3}),
            'possibility_of_hazardous_reactions': forms.Textarea(attrs={'rows': 3}),
            'conditions_to_avoid': forms.Textarea(attrs={'rows': 3}),
            'incompatible_materials': forms.Textarea(attrs={'rows': 3}),
            'hazardous_decomposition_products': forms.Textarea(attrs={'rows': 3}),
        }

class MSDSSection11Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'inhalation_route',
            'ingestion_route',
            'skin_contact_route',
            'eye_contact_route',
            'symptoms',
            'delayed_effects',
            'immediate_effects',
            'chronic_effects',
            'acute_toxicity_estimates',
        ]

        widgets = {
            'inhalation_route': forms.Textarea(attrs={'rows': 3}),
            'ingestion_route': forms.Textarea(attrs={'rows': 3}),
            'skin_contact_route': forms.Textarea(attrs={'rows': 3}),
            'eye_contact_route': forms.Textarea(attrs={'rows': 3}),
            'symptoms': forms.Textarea(attrs={'rows': 5}),
            'delayed_effects': forms.Textarea(attrs={'rows': 3}),
            'immediate_effects': forms.Textarea(attrs={'rows': 3}),
            'chronic_effects': forms.Textarea(attrs={'rows': 3}),
            'acute_toxicity_estimates': forms.Textarea(attrs={'rows': 2}),
        }


class MSDSSection12Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'ecotoxicity',
            'persistence_and_degradability',
            'bioaccumulative_potential',
            'mobility_in_soil',
            'other_adverse_effects',
        ]
        widgets = {
            'ecotoxicity': forms.Textarea(attrs={'rows': 3}),
            'persistence_and_degradability': forms.Textarea(attrs={'rows': 3}),
            'bioaccumulative_potential': forms.Textarea(attrs={'rows': 3}),
            'mobility_in_soil': forms.Textarea(attrs={'rows': 3}),
            'other_adverse_effects': forms.Textarea(attrs={'rows': 3}),
        }


class MSDSSection13Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'disposal_methods'
        ]
        widgets = {
            'disposal_methods': forms.Textarea(attrs={'rows': 3}),
        }

class MSDSSection14Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'UN_number',
            'UN_proper_shipping_name',
            'transport_hazard_class',
            'packing_group',
            'environmental_hazards',
            'special_precautions',
            'transport_in_bulk',
            'UN_picto'
        ]
        widgets = {
            'UN_number': forms.TextInput(attrs={}),
            'UN_proper_shipping_name': forms.TextInput(attrs={}),
            'transport_hazard_class': forms.TextInput(attrs={}),
            'packing_group': forms.TextInput(attrs={}),
            'environmental_hazards': forms.Textarea(attrs={'rows': 2}),
            'special_precautions': forms.Textarea(attrs={'rows': 2}),
            'transport_in_bulk': forms.Textarea(attrs={'rows': 2}),
        }


class MSDSSection15Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'safety_health_environmental_regulations',
        ]
        widgets = {
            'safety_health_environmental_regulations': forms.Textarea(attrs={'rows': 3}),
        }

class MSDSSection16Form(forms.ModelForm):
    class Meta:
        model = MSDS
        fields = [
            'date_of_preparation',
            'last_revision_date',
            'disclaimer',
            'version',
            'other_information'
        ]
        widgets = {
            'date_of_preparation': forms.SelectDateWidget(years=range(2000, 2031)),
            'last_revision_date': forms.SelectDateWidget(years=range(2000, 2031)),
            'disclaimer': forms.Textarea(attrs={'rows': 3}),
            'version': forms.TextInput(attrs={}),
            'other_information': forms.Textarea(attrs={'rows': 3})
        }
