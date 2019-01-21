from django.contrib import admin

import pinpon.models as models
import pinpon.ranking as ranking

class PlayerAdmin(admin.ModelAdmin):
    readonly_fields = ('rank',)
    list_display = ('rank', 'name',)
    list_display_links = ('name',)

    def rank(self, obj):
        ranks = ranking.current()
        return ranking.rank(ranks, obj)

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
