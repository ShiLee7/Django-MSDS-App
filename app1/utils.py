import requests
import unicodedata
import re
from pubchem_api_crawler import Annotations
from .constants import *

import logging

from PIL import Image, ImageOps
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.units import inch
from reportlab.platypus import Flowable
from reportlab.lib.utils import ImageReader

logger = logging.getLogger(__name__)

def find_svg_urls(obj, svg_data=None):
    if svg_data is None:
        svg_data = set()  # Use a set to store unique tuples of (url, description)

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'Markup' and isinstance(value, list):
                for item in value:
                    if item.get('Type') == 'Icon' and item.get('URL', '').endswith('.svg'):
                        url = item['URL']
                        description = item.get('Extra', 'GHS Label')
                        svg_data.add((url, description))  # Add tuple to the set
            else:
                find_svg_urls(value, svg_data)

    elif isinstance(obj, list):
        for item in obj:
            find_svg_urls(item, svg_data)

    return svg_data

def fetch_and_find_svg_urls(cid):
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?response_type=display&heading=GHS%20Classification'
    response = requests.get(url)

    if response.status_code != 200:
        logger.debug(f"Failed to fetch svg data for CID {cid}. Status code: {response.status_code}")

        return ''

    data = response.json()
    svg_data_set = find_svg_urls(data)

    # Convert set of tuples back to list of dictionaries
    svg_data = [{'url': url, 'description': description} for url, description in svg_data_set]

    return svg_data

def get_cid_from_cas(cas_number):
    """
    Fetch the PubChem CID for a given CAS number.

    Parameters:
        cas_number (str or int): The CAS number of the compound.

    Returns:
        int: The CID of the compound, or None if not found.
    """
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas_number}/cids/JSON'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    cids = data.get('IdentifierList', {}).get('CID', [])
    if not cids:
        return None
    return cids[0]  # Return the first CID

def get_classification_from_cid(cid):
    """
    Fetch the classification data from PubChem using the CID.
    """
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Hazard Classes and Categories')
        # Assuming the classification is in the first row and second column
        classification = annotations.iloc[2, 0]
        return classification
    except Exception as e:
        # Handle exceptions (e.g., data not found)
        return None

def get_signal_word(cid):
    """
    Fetches and normalizes the signal word for a given CID from GHS Classification annotations.
    
    Parameters:
        cid (int): Compound ID.
    
    Returns:
        str or None: The normalized signal word ("warning" or "danger"), or None if not found.
    """
    try:
        # Fetch annotations
        annotations = Annotations().get_compound_annotations(cid, heading='GHS Classification')
        
        # Check if annotations DataFrame has the required structure
        if annotations.shape[0] < 3:
           return 'Warning'
        
        # Extract signal word from annotations
        signal_word = annotations.iloc[2, 0]
        
        # Normalize string
        def normalize_string(input_string):
            # Convert to lowercase and strip whitespace
            normalized_string = input_string.lower().strip()
            # Remove accents/diacritics
            normalized_string = unicodedata.normalize('NFD', normalized_string)
            return ''.join(c for c in normalized_string if unicodedata.category(c) != 'Mn')
        
        # Normalize and validate the signal word
        signal_word = normalize_string(signal_word)
        logger.warning(signal_word)
        if signal_word == 'warning':
            return 'Warning'
        elif signal_word == 'danger':
            return 'Danger'
        else:
            return 'Warning'
    
    except Exception as e:
        # Log or handle exceptions (optional logging can be added)
        logger.warning(f"Error fetching signal word for CID {cid}: {e}")
        return 'Warning'

def get_p_codes(cid):
    try:
        # Fetch annotations
        annotations = Annotations().get_compound_annotations(cid, heading='GHS Classification')

        # Ensure annotations have enough data
        if annotations.shape[0] > 4 and annotations.shape[1] > 0:
            p_codes = annotations.iloc[4, 0]
        else:
            logger.warning(f"P-codes not found in annotations for CID {cid}")
            return None

        # Clean and split P-codes
        p_codes_cleaned = p_codes.replace(';', ',').replace(' and ', ', ')
        p_codes_list = [code.strip() for code in p_codes_cleaned.split(',')]

        # Initialize dictionaries
        general_p = {}
        prevention_p = {}
        response_p = {}
        storage_p = {}
        dispose_p = {}

        def find_p_code_description(p_code):
            for category in PRECAUTIONARY_STATEMENTS.values():
                if p_code in category:
                    return category[p_code]
            return ''  # If not found

        for p_code in p_codes_list:
            # Correct regex matching
            match = re.match(r'P(\d+)', p_code)
            if match:
                prefix_number = match.group(1)
                group_prefix = prefix_number[0]  # First digit
                # Find description
                description = find_p_code_description(p_code)
                if description:
                    if group_prefix == '1':
                        general_p[p_code] = description
                    elif group_prefix == '2':
                        prevention_p[p_code] = description
                    elif group_prefix == '3':
                        response_p[p_code] = description
                    elif group_prefix == '4':
                        storage_p[p_code] = description
                    elif group_prefix == '5':
                        dispose_p[p_code] = description
                else:
                    logger.warning(f"Description not found for P-code: {p_code}")
            else:
                logger.warning(f"Invalid P-code format: {p_code}")

        # Combine all codes
        all_codes = {
            'general': general_p,
            'prevention': prevention_p,
            'response': response_p,
            'storage': storage_p,
            'disposal': dispose_p,
        }

        logger.debug(f"P-codes categorized: {all_codes}")
        return all_codes

    except Exception as e:
        logger.error(f"Error fetching P-codes for CID {cid}: {e}")
        return None

def get_h_codes(cid):
    try:
        # Fetch annotations
        annotations = Annotations().get_compound_annotations(cid, heading='GHS Classification')

        # Ensure annotations have enough data
        if annotations.shape[0] > 3 and annotations.shape[1] > 0:
            h_codes = annotations.iloc[3, 0]
        else:
            logger.warning(f"H-codes not found in annotations for CID {cid}")
            return None

        # Clean and split H-codes
        h_codes_cleaned = [
            re.sub(r"\s*\(.*?\)", "", part.strip())
            for part in h_codes.split(';') if part.strip()
        ]

        logger.debug(f"H-codes categorized: {h_codes_cleaned}")
        return h_codes_cleaned
    
    except Exception as e:
        logger.error(f"Error fetching H-codes for CID {cid}: {e}")
        return None


def get_synonyms_from_cas(cas):
    """
    Retrieve all possible synonyms for a compound using its CAS number via the PubChem API.

    Args:
        cas_number (str): The CAS number of the compound.

    Returns:
        list: A list of synonyms for the compound or an empty list if not found.
    """
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/synonyms/TXT"

    try:
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            synonyms = [line.strip() for line in response.text.splitlines() if line.strip()]
            logger.info(f"Retrieved {len(synonyms)} synonyms for CAS number {cas}")
            return synonyms
        else:
            logger.warning(f"Failed to retrieve synonyms. HTTP Status Code: {response.status_code}")
            logger.warning(f"Response content: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during API request: {e}")
        return []

def get_first_aid(cid):
    annotations = Annotations().get_compound_annotations(cid, heading='First Aid Measures')
    if not annotations.empty:
        # Extract the first column by position and convert it to a list
        return annotations.iloc[:, 0].dropna().tolist()
        logger.debug(annotations.iloc[:, 0].dropna().tolist())
    else:
        return []

def get_iupac(cas):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/IUPACName,Title/json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Navigate to the IUPACName key
            iupac = data["PropertyTable"]["Properties"][0]["IUPACName"]
            logger.debug(iupac)
            return iupac
        else:
            logger.error(f"Error: Unable to fetch chemical name (Status Code: {response.status_code})")
            return ''


    except Exception as e:
        return f"Error: {str(e)}"

def get_fire(cid):
    annotations = Annotations().get_compound_annotations(cid, heading='Fire Fighting Procedures')
    if not annotations.empty:
        # Extract the first column by position and convert it to a list
        return annotations.iloc[:, 0].dropna().tolist()
        logger.debug(annotations.iloc[:, 0].dropna().tolist())
    else:
        return []

def get_acci(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Accidental Release Measures')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []
    except AttributeError as e:
        logger.error(f"Error fetching 'Accidental Release Measures' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_hand_stor(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Handling and Storage')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []
    except AttributeError as e:
        logger.error(f"Error fetching 'Handling and Storage' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_safe_stor(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Safe Storage')
        if not annotations.empty:
            # Extract the first column, drop nulls, and return a newline-separated string
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return '\n'.join(safe_storage_list)  # Convert list to newline-separated string
        else:
            return ''
    except AttributeError as e:
        logger.error(f"Error fetching 'Safe Storage' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_oel(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Occupational Exposure Limits (OEL)')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []
    except AttributeError as e:
        logger.error(f"Error fetching 'Occupational Exposure Limits (OEL)' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_phys(cid):
     try:
        annotations = Annotations().get_compound_annotations(cid, heading='Physical Description')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

     except AttributeError as e:
        logger.error(f"Error fetching 'Physical Description' data for CID {cid}: {e}")
        return []
     except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_odor(cid):
     try:
        annotations = Annotations().get_compound_annotations(cid, heading='Odor')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

     except AttributeError as e:
        logger.error(f"Error fetching 'Odor' data for CID {cid}: {e}")
        return []
     except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_melt(cid):
     try:
        annotations = Annotations().get_compound_annotations(cid, heading='Melting Point')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

     except AttributeError as e:
        logger.error(f"Error fetching 'Melting Point' data for CID {cid}: {e}")
        return []
     except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_boil(cid):
     try:
        annotations = Annotations().get_compound_annotations(cid, heading='Boiling Point')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

     except AttributeError as e:
        logger.error(f"Error fetching 'Boiling Point' data for CID {cid}: {e}")
        return []
     except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_flame(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Flammable Limits')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Flame' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_flash(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Flash Point')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Flash Point' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_autoig(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Autoignition Temperature')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Autoignition Temperature' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_pH(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='pH')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'pH' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_solu(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Solubility')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Solubility' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_vap_p(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Vapor Pressure')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Vapor Pressure' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_vap_d(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Vapor Density')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return []

    except AttributeError as e:
        logger.error(f"Error fetching 'Vapor Density' data for CID {cid}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return []

def get_reac(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Reactivity Profile')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Reactivity Profile' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_h_reac(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Other Hazardous Reactions')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Other Hazardous Reactions' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_h_decomp(cid):
     try:
        annotations = Annotations().get_compound_annotations(cid, heading='Decomposition')
        if annotations is not None and hasattr(annotations, "empty") and not annotations.empty:
            value = annotations.iloc[0, 0]
            logger.debug(value)
            return value
        else:
            return ''

     except AttributeError as e:
        logger.error(f"Error fetching 'Decomposition' data for CID {cid}: {e}")
        return ''
     except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return '' 

def process_statements(field_value):
    if field_value:
        # Split and clean the input field
        statement_list = [stmt.strip() for stmt in field_value.split(';') if stmt.strip()]
        if statement_list:
            # Create bullet-pointed HTML-compatible string
            return ''.join([f'• {stmt}<br/>' for stmt in statement_list])
    return ''  # Return empty string if the field is empty or contains no valid statements

def get_un(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='UN number')
        if not annotations.empty:
            # Extract the first column, drop nulls, and return a newline-separated string
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return '\n'.join(safe_storage_list)  # Convert list to newline-separated string
        else:
            return ''
    except AttributeError as e:
        logger.error(f"Error fetching 'UN number' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_shipping_name(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Shipping Name/ Number DOT/UN/NA/IMO')
        if not annotations.empty:
            # Extract the first column, drop nulls, and return a newline-separated string
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return '\n'.join(safe_storage_list)  # Convert list to newline-separated string
        else:
            return ''
    except AttributeError as e:
        logger.error(f"Error fetching 'Shipping Name/ Number DOT/UN/NA/IMO' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def irritants(cid):
    try:
        annotations = Annotations().get_compound_annotations(cid, heading='Skin, Eye, and Respiratory Irritations')
        if not annotations.empty:
            # Extract the first column, drop nulls, and return a newline-separated string
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return '\n'.join(safe_storage_list)  # Convert list to newline-separated string
        else:
            return ''
    except AttributeError as e:
        logger.error(f"Error fetching 'Skin, Eye, and Respiratory Irritations' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_tox_data(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Toxicity Data')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Toxicity Data' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_form(self, step=None, data=None, files=None):
        if data:
            # Log the submitted data for the current step
            logger.debug(f"Submitted data for step {step}: {data}")

def get_eco_tox(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Ecotoxicity Values')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Ecotoxicity Values' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_other_eco(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Ecotoxicity Excerpts')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Ecotoxicity Excerpts' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_ch_eff(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Adverse Effects')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Adverse Effects' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_immi_eff(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Acute Effects')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Acute Effects' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_bio_accu(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Biological Half-Life')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Biological Half-Life' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_mob_soil(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Soil Adsorption/Mobility')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Soil Adsorption/Mobility' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

def get_degra(cid):
    try:

        annotations = Annotations().get_compound_annotations(cid, heading='Environmental Biodegradation')

        if not annotations.empty:
            
            safe_storage_list = annotations.iloc[:, 0].dropna().tolist()
            logger.debug(safe_storage_list)
            return ';'.join(safe_storage_list) 

        else:
            return ''

    except AttributeError as e:
        logger.error(f"Error fetching 'Environmental Biodegradation' data for CID {cid}: {e}")
        return ''
    except Exception as e:
        logger.error(f"An unexpected error occurred for CID {cid}: {e}")
        return ''

class RotatedImage(Flowable):
    def __init__(self, path, angle=45, scale=0.75):
        """
        :param path: The filesystem path to the image.
        :param angle: The rotation angle in degrees (counterclockwise).
        :param scale: A scaling factor to reduce or enlarge the image.
                      For example, 0.75 means 75% of the original size.
        """
        Flowable.__init__(self)
        self.path = path
        self.angle = angle
        self.scale_factor = scale

    def wrap(self, availWidth, availHeight):
        img_reader = ImageReader(self.path)
        self.iw, self.ih = img_reader.getSize()
        # The actual space occupied after scaling
        return (self.iw * self.scale_factor, self.ih * self.scale_factor)

    def draw(self):
        # Save the current canvas state
        self.canv.saveState()

        # Translate to the center of what will be the final scaled image
        self.canv.translate((self.iw * self.scale_factor) / 2.0,
                            (self.ih * self.scale_factor) / 2.0)

        # Rotate around the center
        self.canv.rotate(-self.angle)

        # Now scale down the image
        self.canv.scale(self.scale_factor, self.scale_factor)

        # Draw the image centered at the origin (0,0)
        # Since we've rotated and scaled the canvas, we draw the image with no w/h specified.
        self.canv.drawImage(self.path, -self.iw/2.0, -self.ih/2.0)

        # Restore the canvas to its previous state
        self.canv.restoreState()













