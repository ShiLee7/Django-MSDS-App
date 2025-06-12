# Django MSDS App

## Overview

The Django MSDS App is a sophisticated application designed to generate comprehensive Safety Data Sheets (SDS) for chemicals. The idea for this app occurred to me because, as a chemical engineer, I experienced firsthand the challenges of obtaining accurate and complete chemical data for substances. By integrating user-provided information with dynamic data retrieved from public sources, this platform offers a highly professional solution for obtaining critical chemical safety information. Additionally, the project includes several landing pages aimed at promoting my services, enhancing accessibility and visibility for potential clients.

### What is an SDS (Safety Data Sheet)?

For context, a **Safety Data Sheet (SDS)** is a document that provides critical information about hazardous chemicals, helping ensure workplace safety and compliance with regulations. SDSs are required by regulatory agencies worldwide, such as **OSHA (Occupational Safety and Health Administration)** in the U.S. and **REACH (Registration, Evaluation, Authorisation, and Restriction of Chemicals)** in the EU.

An SDS outlines essential information about chemical properties, hazards, safe handling, storage, and emergency measures in case of an accident. It is a fundamental component of the **Globally Harmonized System of Classification and Labeling of Chemicals (GHS)**.

Under GHS, an **SDS must contain 16 sections**.

The **Django MSDS App** streamlines SDS creation, automatically retrieving chemical data from trusted sources and structuring it in compliance with **GHS standards**. This tool simplifies the process of obtaining critical chemical safety information for professionals worldwide.


## Distinctiveness and Complexity

The distinctiveness of this project stems from its innovative integration of real-time chemical data with a user-friendly, multi-step form workflow. Key features include:

- **Dynamic Data Integration:**  
  Each section of the SDS initiates an API call to the U.S. Environmental Protection Agency's PubChem database via a API crawler. The system fetches detailed chemical information—ranging from hazard classifications to synonyms and pictograms—that would otherwise require expensive tests or extensive research.

- **Intelligent Identifier Mapping:**  
  While the chemical industry predominantly uses the CAS number as the primary identifier, PubChem operates using the unique CID (Compound Identifier). In Section 1, the app captures and stores the CAS number and then converts it to the corresponding CID. This conversion enables all subsequent API calls to seamlessly retrieve accurate chemical data.

- **Multi-Step Form Workflow:**  
  The Django **`formtools.wizard.views.SessionWizardView`** enables breaking large forms into **smaller, manageable sections**, all under a **single URL path** (`path:/msds/create`). This approach is particularly beneficial for SDS generation, as it ensures **logical progression** through the **16 sections** of the document.

- **Professional PDF Generation:**  
  Upon completion of the data entry process, the application aggregates the data from all sections and creates a new SDS record in the MSDS model. Each Safety Data Sheet—containing critical details like product identification, hazard information, composition, first‐aid measures, and more—is stored in the database for future reference. The pdf is created by leveraging the ReportLab library. Using ReportLab’s BaseDocTemplate along with platypus components (such as Paragraph, Table, Spacer, and custom flowables), the SDS data is transformed into a well-structured document. Custom styles and layouts—including headers, footers, watermarks, and even rotated images for pictograms—ensure that all critical information is clearly and attractively presented. Finally, the generated PDF is delivered as a downloadable HTTP response, providing a complete and ready-to-use Safety Data Sheet.

- **Internationalization and Translation (i18n):**
  To reach a wider audience, the entire webpage is equipped with Django’s internationalization framework (i18n), allowing seamless translation of all content into Spanish. This feature ensures that Spanish speaking users can easily navigate and utilize the platform, making critical chemical safety information accessible to a global user base.

Even if users do not require a complete SDS document, many individual pieces of chemical data are challenging to obtain. For instance, determining a chemical’s mobility in soil typically requires costly testing or an extensive literature review. One of the primary objectives of this app is to provide a user-friendly platform that simplifies access to comprehensive chemical information.

### **How Django Wizard Forms Work in the MSDS App** 
1. **User begins SDS creation** at `/msds/create`. 
2. **Each section is displayed sequentially** using Django’s `SessionWizardView`. 
3. **Form data is stored in the session**, reducing unnecessary database writes. 
4. **Dynamic API calls** auto-fill specific sections with the CAS number  provided in the first section. 
5. **Users can navigate between steps**, ensuring accuracy before submission. 
6. On completion, all data is validated and stored in the MSDS model. 
7. **A professional PDF is generated** using ReportLab.

## Installation

Follow these steps to install and run the Django MSDS App locally: 

#### 1. Clone the Repository

#### 2. Create a Virtual Environment

#### 3. Install Dependencies

```
pip install -r requirements.txt
```
#### 4. Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create a Superuser (Optional, for admin access)
```
python manage.py createsuperuser
```
#### 6. Run the Development Server
```
python manage.py runserver
```
#### 7. Access the Application
Open your browser and navigate to http://127.0.0.1:8000/
##
For internationalization, ensure that you have configured Django's i18n settings in your `settings.py` (check the file in the repo) and have the necessary translation files for Spanish. You can compile the translations with:
```
python manage.py compilemessages
```
## Files & Project Structure Overview

Below is an overall description of the project structure and main files.

### Root Directory
- **manage.py:**  
  The main Django management script used to run commands (e.g., `runserver`, `migrate`, etc.).

- **requirements.txt:**  
  Contains a list of the Python package dependencies required for the project.

- **Project Configuration Folder (SUN):**  
  This folder includes:
  - **settings.py:**  
    Contains all the Django settings and configuration.
  - **urls.py:**  
    Defines the URL routing for the project, here the i18n translation tool is configured so that the language code act as prefix to every url path defined at app level.



### App Directory (`app1`)
This directory contains the core functionality of the Django MSDS App.

- **constants.py:**  
  Stores constant values used throughout the project, such as pictogram URLs and precautionary statements.

- **forms.py:**  
  Contains Django ModelForm classes for each SDS section (e.g., `MSDSSection1Form`, `MSDSSection2Form`, etc.).  
  These forms are used in the multi-step form wizard to capture and validate data for every section of an SDS.

- **models.py:**  
  Defines the `MSDS` model, which represents a Safety Data Sheet record and stores the chemical safety information gathered through the app.

- **tests.py:**  
  Includes the main unit test to verify that the application functions as expected, using Selenium and the Chrome Driver as taught on the course.

- **utils.py:**  
  Provides a collection of helper functions that:
  - **Retrieve Chemical Data:**  
    Fetches data from public APIs (e.g., converting CAS numbers to CIDs, retrieving hazard information).
  - **Process and Format Data:**  
    Works with Pandas DataFrames returned from API calls to extract and transform data by:
    - Using DataFrame indexing (e.g., `iloc[2, 0]`) to pick specific values like hazard statements or signal words.
    - Converting these extracted values into plain strings that are easily rendered in HTML.
    - Applying formatting functions (such as `process_statements`) to transform delimited text into bullet-point lists with HTML breaks.

#### Views Module Organization

Within the `views` directory, the view logic has been separated into three distinct files for better modularity and maintainability:

#### 1. `gen_views.py`
- Contains general view functions such as rendering the home page, error pages, and other auxiliary endpoints.
- Isolates common functionality from the more complex logic, ensuring cleaner and more maintainable code.

#### 2. `sds_pdf_view.py`
- Houses the main logic for generating the SDS PDF using ReportLab.
- Responsible for assembling the SDS data, applying custom ReportLab components (like `BaseDocTemplate`, `Paragraph`, `Table`, etc.), and delivering the generated PDF as a downloadable HTTP response.
- Focuses solely on transforming the collected SDS data into a professional, well-structured PDF document.

#### 3. `sds_wizard_view.py`
- Contains the primary logic for the multi-step form wizard (leveraging Django’s `SessionWizardView`).
- Manages the progressive data collection across the 16 SDS sections, ensuring that each form is validated and that data is stored in the session.
- Coordinates the final submission process that aggregates all data and creates an SDS record in the database.

#### 4. `__init__.py`
- This file marks the `views` directory as a Python package.
- Enables organized and structured imports of the view modules throughout the application.

#### JavaScript Files Overview

This project uses vanilla JavaScript in the front-end to handle dynamic form interactions and data processing. The js files are:

- **c_syn.js:**  
  Manages the synonyms dropdown functionality. It toggles the display of a custom synonym input when the "custom" option is selected and ensures the custom value is added to the dropdown on form submission.

- **precautionary_statements.js:**  
  Dynamically handles precautionary statement fields in Section 2. It reads initial statement data, creates input fields for each category (general, prevention, response, storage, disposal), and aggregates these inputs into a hidden field before form submission.

- **cn.js:**  
  Provides functionality to add or remove concentration fields in Section 3. It collects individual concentration inputs and combines them into a single string to update the corresponding hidden field upon form submission.

- **UN_picto.js:**  
  Facilitates the selection of UN pictograms in Section 14. It listens for the update button click, gathers image sources from selected checkboxes, and updates a hidden field with the selected pictogram data.

- **classification.js:**  
  Manages classification input fields in Section 2. It splits the initial classification value, dynamically generates individual input fields for each entry, and aggregates them into a hidden field before form submission.

- **focus_message.js:**  
  Displays a focus message when a specific textarea (e.g., for acute toxicity estimates) gains focus, and hides the message when the textarea loses focus.

- **h_codes.js:**  
  Dynamically creates and manages hazard statement input fields based on the initial hazard data. It allows users to add or remove inputs and aggregates the values into a hidden field prior to form submission.

- **picto.js:**  
  Coordinates pictogram selection and display. It reads auto-populated pictogram data and additional pictogram options from the page, ensures no duplicates by combining selections, and updates both the visual display and a hidden field with the final pictogram list.



#### Templates Directory
Django templates are used to render the HTML pages. 

- **msds_section.html:**  
  Templates for each SDS section using the multi-step form wizard (e.g., `msds_section1.html`, `msds_section2.html`, etc.).

The project leverages reusable HTML snippets to keep the code clean and maintain a consistent design (_contact.html & _form_snippet.html). These snippets are incorporated into the main templates using Django’s `{% include %}` tag, ensuring that updates to these elements propagate throughout the site effortlessly.

#### Selenium Test for MSDS Wizard Form

The file called: tests.py was used in the showcase video to display the funcionality of the app. The test class `WizardFormSeleniumTests` uses `StaticLiveServerTestCase` to launch a temporary live server and initialize a Chrome WebDriver with settings that enable silent PDF downloads and external viewing of PDFs.

The test method `test_msds_create_wizard_full` first visits several landing pages (`home`, `iq`, `edu`, `about`), selects "English" from a dropdown, scrolls to simulate user behavior, and then navigates to the MSDS creation form. It sequentially fills in required fields across all 16 MSDS sections—ranging from identification and hazards to transport and disposal—and submits the completed form. It also includes robust handling for stale elements and scrolling actions to ensure reliability during interaction.

After form submission, the test waits for the PDF download to complete, confirms its presence, and copies it to a permanent directory.

This streamlined testing approach ensures that both the form functionality and PDF generation work as intended.

## Third Party Code

The project integrates valuable third-party code and resources, including:

- **PubChem Database and API:**  
  The app leverages the PubChem database to retrieve essential chemical data such as compound identifiers (CIDs), hazard classifications, and other related information. Public API endpoints are used to access and integrate this data seamlessly.

- **API Crawler:**  
  The project makes use of the [PubChem API Crawler](https://github.com/jonasrenault/pubchem-api-crawler?tab=readme-ov-file) by Jonas Renault. This tool simplifies querying the PubChem API and extracting the necessary data from its responses, making the integration process more efficient.

- **Media and Icons:**  
  Several icons and media assets, such as the GHS pictograms, are sourced from reputable public sources such as: https://www.osha.gov/hazcom/pictograms
