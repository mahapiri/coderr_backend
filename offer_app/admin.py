from django.contrib import admin

from offer_app.models import Feature, Offer, OfferDetail


# Registers Offer, OfferDetail, and Feature models in the Django admin site.
admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Feature)
