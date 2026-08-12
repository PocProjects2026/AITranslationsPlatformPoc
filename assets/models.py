from django.db import models

class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    valuation = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
