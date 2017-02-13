from django.contrib import admin

# Register your models here.

from .models import SandboxPositions, LcoptExternalInputExchange, LcoptExternalOutputExchange, LcoptIntermediateExchange, LcoptModel, LcoptProcess

admin.site.register(SandboxPositions)
admin.site.register(LcoptExternalInputExchange)
admin.site.register(LcoptExternalOutputExchange)
admin.site.register(LcoptIntermediateExchange)
admin.site.register(LcoptModel)
admin.site.register(LcoptProcess)
