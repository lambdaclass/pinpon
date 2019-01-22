from django.contrib import admin
from django import forms

import pinpon.models as models
import pinpon.ranking as ranking

class PlayerAdmin(admin.ModelAdmin):
    readonly_fields = ('rank', 'points')
    list_display = ('rank', 'name', 'points')
    list_display_links = ('name',)

    def rank(self, obj):
        if obj.pk:
            current = ranking.current()
            return ranking.rank(current, obj)[0]

    def points(self, obj):
        if obj.pk:
            current = ranking.current()
            return ranking.rank(current, obj)[1]

class SetInline(admin.TabularInline):
    model = models.Set

class MatchForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['player1'] == cleaned_data['player2']:
            raise forms.ValidationError("Players should be different!")

        return cleaned_data

class MatchAdmin(admin.ModelAdmin):
    form = MatchForm

    inlines = (SetInline,)
    readonly_fields = ('winner',)
    list_display = ('date', '__str__', 'winner')
    list_display_links = ('__str__',)
    ordering = ('-date',)

admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Match, MatchAdmin)

# Register your models here.
