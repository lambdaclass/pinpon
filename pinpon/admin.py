from django.contrib import admin
from django import forms

import pinpon.models as models
from pinpon.ranking import EloRankingStrategy

class PlayerForm(forms.ModelForm):

    def clean_slack_username(self):
        return self.cleaned_data['slack_username'].strip('@')

    def clean_slack_emoji(self):
        return self.cleaned_data['slack_emoji'].strip(':')

class PlayerAdmin(admin.ModelAdmin):
    form = PlayerForm

    readonly_fields = ('rank', 'points')
    list_display = ('rank', 'name', 'points')
    list_display_links = ('name',)

    def rank(self, obj):
        if obj.pk:
            ranking = EloRankingStrategy()
            return ranking.rank(obj)

    def points(self, obj):
        if obj.pk:
            ranking = EloRankingStrategy()
            return ranking.points(obj)

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
