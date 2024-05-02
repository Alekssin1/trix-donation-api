from django.contrib import admin

from .models import MoneyCollection, Report, ReportImage, ReportVideo, MoneyCollectionRequisites, OtherRequisite, BankCard


admin.site.register(MoneyCollection)
admin.site.register(Report)
admin.site.register(ReportImage)
admin.site.register(ReportVideo)
admin.site.register(MoneyCollectionRequisites)
admin.site.register(OtherRequisite)
admin.site.register(BankCard)
