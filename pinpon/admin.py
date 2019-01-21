from django.contrib import admin
from django import forms

import pinpon.models as models
import pinpon.ranking as ranking

class PlayerAdmin(admin.ModelAdmin):
    readonly_fields = ('rank', 'points')
    list_display = ('rank', 'name',)
    list_display_links = ('name',)

    def rank(self, obj):
        current = ranking.current()
        return ranking.rank(current, obj)[0]

    def points(self, obj):
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

    def save(self, commit=True):
        # populate ranking related fields
        instance = super(MatchForm, self).save(commit=False)
        current = ranking.current()

        instance.player1_rank, instance.player1_points = ranking.rank(current, instance.player1)
        instance.player2_rank, instance.player2_points = ranking.rank(current, instance.player2)

        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.Match
        fields = ('date', 'player1', 'player2')


class MatchAdmin(admin.ModelAdmin):
    form = MatchForm

    inlines = (SetInline,)
    readonly_fields = ('winner', 'p1_rank', 'p2_rank')
    list_display = ('date', '__str__')
    list_display_links = ('__str__',)

    def p1_rank(self, obj):
        return '#{} ({} points)'.format(obj.player1_rank, obj.player1_points)

    def p2_rank(self, obj):
        return '#{} ({} points)'.format(obj.player2_rank, obj.player2_points)


admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Match, MatchAdmin)

# Register your models here.
