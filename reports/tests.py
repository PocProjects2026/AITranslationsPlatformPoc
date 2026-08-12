import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from assets.models import Asset

class ReportAPITests(TestCase):
    def setUp(self):
        Asset.objects.create(name="Laptop", asset_type="Hardware", status="Active", valuation=1200.00)
        Asset.objects.create(name="Server", asset_type="Hardware", status="Maintenance", valuation=5000.00)

    def test_health_check(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_unsupported_language(self):
        response = self.client.post(reverse('asset-report'), data={"language": "es"}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["supported_languages"], ["en", "fr", "de"])

    def test_pdf_generation_english(self):
        response = self.client.post(reverse('asset-report'), data={"language": "en"}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Verify HTML content passed to weasyprint or returned as fallback
        html_string = response.content.decode('utf-8')
        self.assertIn("Asset Management Report", html_string)
        self.assertIn("Laptop", html_string)

    def test_pdf_generation_french(self):
        response = self.client.post(reverse('asset-report'), data={"language": "fr"}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        html_string = response.content.decode('utf-8')
        self.assertIn("Rapport de Gestion des Actifs", html_string)

    def test_pdf_generation_german(self):
        response = self.client.post(reverse('asset-report'), data={"language": "de"}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        html_string = response.content.decode('utf-8')
        self.assertIn("Vermögensverwaltungsbericht", html_string)
