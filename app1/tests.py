import os
import time
import tempfile
import shutil
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WizardFormSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a temporary directory for downloads
        cls.download_dir = tempfile.mkdtemp()

        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": cls.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True  # disable built-in PDF viewer
        }
        options.add_experimental_option("prefs", prefs)
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        #shutil.rmtree(cls.download_dir)
        super().tearDownClass()

    def test_msds_create_wizard_full(self):
        # Build the URL using the live server and reverse resolution.
        url = self.live_server_url + reverse('msds_create')
        self.driver.get(url)

        # --- Sección 1: Identificación ---
        header1 = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header1.text, "Sección 1: Identificación")
        cas_input = self.driver.find_element(By.ID, "id_section1-cas_number")
        cas_input.send_keys("108-88-3")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 2: Identificación de Peligros ---
        header2 = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header2.text, "Sección 2: Identificación de Peligros")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 3: Composición/Información sobre los ingredientes ---
        header3 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header3.text, "Sección 3: Composición/Información sobre los ingredientes")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 4: Medidas de primeros auxilios ---
        header4 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header4.text, "Sección 4: Medidas de primeros auxilios")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 5: Medidas contra incendios ---
        header5 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header5.text, "Sección 5: Medidas contra incendios")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 6: Medidas en caso de derrames accidentales ---
        header6 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header6.text, "Sección 6: Medidas en caso de derrames accidentales")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 7: Manipulación y Almacenamiento ---
        header7 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header7.text, "Sección 7: Manipulación y Almacenamiento")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 8: Controles de Exposición/Protección Personal ---
        header8 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header8.text, "Sección 8: Controles de Exposición/Protección Personal")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 9: Propiedades físicas y químicas ---
        header9 = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header9.text, "Sección 9: Propiedades físicas y químicas")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 10: Estabilidad y Reactividad ---
        header10 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header10.text, "Sección 10: Estabilidad y Reactividad")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 11: Información Toxicológica ---
        header11 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header11.text, "Sección 11: Información Toxicológica")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 12: Información Ecológica ---
        header12 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header12.text, "Sección 12: Información Ecológica")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 13: Consideraciones sobre la Eliminación ---
        header13 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header13.text, "Sección 13: Consideraciones sobre la Eliminación")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 14: Información sobre el Transporte ---
        header14 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header14.text, "Sección 14: Información sobre el Transporte")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 15: Información Reglamentaria ---
        header15 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(header15.text, "Sección 15: Información Reglamentaria")
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # --- Sección 16: Otra información, incluida la información sobre la preparación y revisión de la HDS ---
        header16 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        self.assertEqual(
            header16.text,
            "Sección 16: Otra información, incluida la información sobre la preparación y revisión de la HDS"
        )
        vr_input = self.driver.find_element(By.ID, "id_section16-version")
        vr_input.send_keys("1")

        # Final click to submit the form
        next_button = self.driver.find_element(By.ID, "wizard_next")
        next_button.click()

        # Optionally, wait for the done.html page to load.
        # For instance, check that the success message is present:
        done_header = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertIn("HDS creación exitosa", done_header.text)

        # Wait for the automatic download to be triggered (triggered by window.onload in the done template)
        pdf_downloaded = False
        timeout = 10  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = os.listdir(self.download_dir)
            if any(file.lower().endswith('.pdf') for file in files):
                pdf_downloaded = True
                break
            time.sleep(1)

        self.assertTrue(pdf_downloaded, "PDF file was not downloaded.")

        # Copy the PDF file(s) to a permanent location for inspection
        pdf_files = [file for file in os.listdir(self.download_dir) if file.lower().endswith('.pdf')]
        if pdf_files:
            permanent_dir = os.path.join(os.getcwd(), 'downloaded_pdfs')
            os.makedirs(permanent_dir, exist_ok=True)
            for pdf in pdf_files:
                shutil.copy(os.path.join(self.download_dir, pdf), permanent_dir)
            # Optionally, verify that the file now exists in the permanent directory
            self.assertTrue(os.path.exists(os.path.join(permanent_dir, pdf_files[0])),
                            "PDF file was not copied to the permanent location.")