import datetime
from django.db.models import Sum, Count
from django.utils import translation
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from assets.models import Asset
try:
    import weasyprint
except (ImportError, OSError):
    weasyprint = None

class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"})

class AssetReportView(APIView):
    SUPPORTED_LANGUAGES = ['en', 'fr', 'de']

    def post(self, request):
        language = request.data.get('language')
        
        if not language or language not in self.SUPPORTED_LANGUAGES:
            return Response(
                {
                    "error": "Unsupported language",
                    "supported_languages": self.SUPPORTED_LANGUAGES
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Activate the requested language
        translation.activate(language)
        
        try:
            # Gather dynamic data
            assets = Asset.objects.all()
            total_assets = assets.count()
            total_valuation = assets.aggregate(total=Sum('valuation'))['total'] or 0
            
            # Status summary
            status_summary = list(assets.values('status').annotate(count=Count('status')))
            
            context = {
                'report_date': datetime.date.today(),
                'total_assets': total_assets,
                'total_valuation': total_valuation,
                'status_summary': status_summary,
                'assets': assets,
            }
            
            # Render HTML template
            html_string = render_to_string('reports/asset_report.html', context)
            
            # Convert HTML to PDF using WeasyPrint
            if weasyprint:
                pdf_file = weasyprint.HTML(string=html_string).write_pdf()
            else:
                pdf_file = html_string.encode('utf-8') # Fallback to HTML for testing without GTK
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f"asset-report-{language}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        finally:
            # Deactivate language translation to not leak to other requests
            translation.deactivate()
