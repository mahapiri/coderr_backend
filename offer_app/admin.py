from django.contrib import admin

from offer_app.models import Feature, Offer, OfferDetail

# Register your models here.
admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Feature)
