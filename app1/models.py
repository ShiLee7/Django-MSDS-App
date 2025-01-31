from django.db import models
from django.utils.translation import gettext_lazy as _

class MSDS(models.Model):
    # Section 1: Identification
    product_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Nombre del Producto"))
    product_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Número de Producto"))
    index_number = models.CharField(max_length=20, blank=True, null=True, default='', verbose_name=_("Número de Índice"))
    reach_no = models.CharField(max_length=20, blank=True, null=True, default='', verbose_name=_("Número de Registro (REACH)"))
    cas_number = models.CharField(max_length=20, default='', verbose_name=_("Número CAS"))
    manufacturer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Nombre del Fabricante"))
    manufacturer_address = models.TextField(blank=True, null=True, verbose_name=_("Dirección del Fabricante"))
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Número de Teléfono"))
    emergency_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Teléfono de Emergencia"))
    recommended_use = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Uso Recomendado"))
    restrictions_on_use = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Restricciones de Uso"))

    # Section 2: Hazard(s) Identification
    classification = models.TextField(blank=True, null=True, verbose_name=_("Clasificación"))
    hazard_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases de Peligro"))
    label_elements = models.JSONField(blank=True, null=True, verbose_name=_("Elementos de Etiqueta"))
    other_hazards = models.TextField(blank=True, null=True, verbose_name=_("Peligros no Clasificados de Otra Manera (HNOC)"))
    general_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases Precautorias Generales"))
    prevention_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases de Prevención"))
    response_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases de Respuesta"))
    storage_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases de Almacenamiento"))
    disposal_statements = models.TextField(blank=True, null=True, verbose_name=_("Frases de Eliminación"))

    SIGNAL_WORD_CHOICES = [
        ('Warning', _("Advertencia")),
        ('Danger', _("Peligro")),
    ]

    signal_word = models.CharField(
        max_length=7,
        choices=SIGNAL_WORD_CHOICES,
        default='Warning',
        verbose_name=_("Palabra de Advertencia")
    )

    # Section 3: Composition/Information on Ingredients
    SUBSTANCE_OR_MIXTURE_CHOICES = [
        ('substance', _("Sustancia")),
        ('mixture', _("Mezcla")),
    ]
    substance_or_mixture = models.CharField(
        max_length=10, choices=SUBSTANCE_OR_MIXTURE_CHOICES, blank=True, null=True,
        verbose_name=_("Sustancia o Mezcla")
    )
    chemical_name = models.CharField(max_length=200, verbose_name=_("Nombre Químico"))
    synonyms = models.TextField(blank=True, null=True, verbose_name=_("Sinónimos"))
    concentration = models.TextField(blank=True, null=True, verbose_name=_("Concentración"))
    other_unique_identifiers = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Otros Identificadores Únicos"))

    # Section 4: First-Aid Measures
    aid_inhal = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Medidas Necesarias para Inhalación")
    )
    aid_inges = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Medidas Necesarias para Ingestión")
    )
    aid_eye = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Medidas Necesarias para Contacto con los Ojos")
    )
    aid_skin = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Medidas Necesarias para Contacto con la Piel")
    )

    symp_inhal = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Síntomas Importantes para Inhalación")
    )
    symp_inges = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Síntomas Importantes para Ingestión")
    )
    symp_eye = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Síntomas Importantes para Contacto con los Ojos")
    )
    symp_skin = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Síntomas Importantes para Contacto con la Piel")
    )

    immediate_attention = models.TextField(
        blank=True, null=True, default='', 
        verbose_name=_("Indicaciones para Atención Médica Inmediata")
    )

    # Section 5: Fire-Fighting Measures
    suitable_extinguishing_media = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Medios de Extinción Adecuados")
    )
    specific_hazards_arising = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Peligros Específicos Derivados del Producto")
    )
    special_protective_actions = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Acciones de Protección Especial")
    )

    # Section 6: Accidental Release Measures
    personal_precautions = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Precauciones Personales")
    )
    protective_equipment = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Equipo de Protección")
    )
    emergency_procedures = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Procedimientos de Emergencia")
    )
    environmental_precautions = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Precauciones Ambientales")
    )
    methods_and_materials_for_containment = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Métodos y Materiales para la Contención")
    )

    # Section 7: Handling and Storage
    precautions_for_safe_handling = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Precauciones para una Manipulación Segura")
    )
    conditions_for_safe_storage = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Condiciones para un Almacenamiento Seguro")
    )

    # Section 8: Exposure Controls/Personal Protection
    control_parameters = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Parámetros de Control")
    )
    appropriate_engineering_controls = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Controles de Ingeniería Apropiados")
    )
    individual_protection_measures = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Medidas de Protección Individual")
    )

    # Section 9: Physical and Chemical Properties
    phys = models.TextField(
        verbose_name=_("Estado Físico/Apariencia")
    )
    colour = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Color")
    )
    odor = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Olor")
    )
    pH = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("pH")
    )
    t_change = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Punto de Fusión/Punto de Congelación")
    )
    boiling_point = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Punto de Ebullición")
    )
    flash_point = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Punto de Inflamación")
    )
    evaporation_rate = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Tasa de Evaporación")
    )
    flammability_information = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Información de Inflamabilidad")
    )
    vapor_pressure = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Presión de Vapor")
    )
    density = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Densidad y/o Densidad Relativa")
    )
    relative_vapour_density = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Densidad Relativa del Vapor")
    )
    solubility = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Solubilidad")
    )
    partition = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Coeficiente de Reparto: n-octanol/agua (valor log)")
    )
    auto_ignition_temperature = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Temperatura de Autoignición")
    )
    decomposition_temperature = models.CharField(
        max_length=40, blank=True, null=True, 
        verbose_name=_("Temperatura de Descomposición")
    )
    kinematic_viscosity = models.CharField(
        max_length=10, blank=True, null=True, 
        verbose_name=_("Viscosidad Cinématica")
    )
    particle_characteristics = models.CharField(
        max_length=10, blank=True, null=True, 
        verbose_name=_("Características de las Partículas")
    )

        # Section 10: Stability and Reactivity
    reactivity = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Reactividad")
    )
    chemical_stability = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Estabilidad Química")
    )
    possibility_of_hazardous_reactions = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Posibilidad de Reacciones Peligrosas")
    )
    conditions_to_avoid = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Condiciones a Evitar")
    )
    incompatible_materials = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Materiales Incompatibles")
    )
    hazardous_decomposition_products = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Productos de Descomposición Peligrosos")
    )

    # Section 11: Toxicological Information
    inhalation_route = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Vía de Exposición: Inhalación"),
        help_text=_("Información sobre la probabilidad de exposición por inhalación.")
    )
    ingestion_route = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Vía de Exposición: Ingestión"),
        help_text=_("Información sobre la probabilidad de exposición por ingestión.")
    )
    skin_contact_route = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Vía de Exposición: Contacto con la Piel"),
        help_text=_("Información sobre la probabilidad de exposición por contacto con la piel.")
    )
    eye_contact_route = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Vía de Exposición: Contacto con los Ojos"),
        help_text=_("Información sobre la probabilidad de exposición por contacto con los ojos.")
    )
    symptoms = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Síntomas Relacionados con las Características"),
        help_text=_("Síntomas relacionados con las características físicas, químicas y toxicológicas.")
    )
    delayed_effects = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Efectos Retardados"),
        help_text=_("Información sobre los efectos retardados de la exposición.")
    )
    immediate_effects = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Efectos Inmediatos"),
        help_text=_("Información sobre los efectos inmediatos de la exposición.")
    )
    chronic_effects = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Efectos Crónicos"),
        help_text=_("Información sobre los efectos crónicos de la exposición a corto y largo plazo.")
    )
    acute_toxicity_estimates = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Estimaciones de Toxicidad Aguda"),
        help_text=_("Medidas numéricas de toxicidad, como estimaciones de toxicidad aguda.")
    )

    # Section 12: Ecological Information (non-mandatory)
    ecotoxicity = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Ecotoxicidad")
    )
    persistence_and_degradability = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Persistencia y Degradabilidad")
    )
    bioaccumulative_potential = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Potencial de Bioacumulación")
    )
    mobility_in_soil = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Movilidad en el Suelo")
    )
    other_adverse_effects = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Otros Efectos Adversos")
    )

    # Section 13: Disposal Considerations (non-mandatory)
    disposal_methods = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Métodos de Eliminación")
    )

    # Section 14: Transport Information (non-mandatory)
    UN_number = models.CharField(
        max_length=50, blank=True, null=True, 
        verbose_name=_("Número ONU")
    )
    UN_proper_shipping_name = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Nombre de Envío Adecuado ONU")
    )
    transport_hazard_class = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name=_("Clase de Peligro para el Transporte")
    )
    packing_group = models.CharField(
        max_length=50, blank=True, null=True, 
        verbose_name=_("Grupo de Embalaje")
    )
    environmental_hazards = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Peligros Ambientales")
    )
    special_precautions = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Precauciones Especiales")
    )
    transport_in_bulk = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Transporte a Granel")
    )
    UN_picto = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Pictograma ONU")
    )

    # Section 15: Regulatory Information (non-mandatory)
    safety_health_environmental_regulations = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Regulaciones de Seguridad, Salud y Medio Ambiente")
    )

    # Section 16: Other Information
    date_of_preparation = models.DateField(
        blank=True, null=True, 
        verbose_name=_("Fecha de Preparación")
    )
    last_revision_date = models.DateField(
        blank=True, null=True, 
        verbose_name=_("Última Fecha de Revisión")
    )
    version = models.CharField(
        blank=True, null=True, max_length=50, 
        verbose_name=_("Versión")
    )
    disclaimer = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Descargo de Responsabilidad")
    )
    other_information = models.TextField(
        blank=True, null=True, 
        verbose_name=_("Otra Información")
    )

