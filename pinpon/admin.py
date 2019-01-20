from django.contrib import admin

import pinpon.models as models

class PlayerAdmin(admin.ModelAdmin):
    # FIXME no textarea for aliases
    pass

class SetInline(admin.TabularInline):
    model = models.Set

class MatchAdmin(admin.ModelAdmin):
    inlines = (SetInline,)
    # TODO validate both players are not equal
    # TODO auto fill ranks and points
    readonly_fields = ('winner',)

admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Match, MatchAdmin)

# Register your models here.
