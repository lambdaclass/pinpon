import collections
from datetime import datetime

from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=150, blank=False)
    aliases = models.CharField(max_length=200, blank=True)
    email = models.EmailField('email address')
    is_active = models.BooleanField('active', default=True)
    slack_username = models.CharField(max_length=30, blank=True)
    slack_emoji = models.CharField(max_length=30, blank=True)

    def alias_list(self):
        return self.aliases.split()

    def __str__(self):
        return str(self.name)


class Set(models.Model):
    match = models.ForeignKey('Match', related_name='sets', on_delete=models.CASCADE)
    player1_points = models.PositiveSmallIntegerField()
    player2_points = models.PositiveSmallIntegerField()

    def winner(self):
        if self.player1_points > self.player2_points:
            return self.match.player1
        elif self.player1_points < self.player2_points:
            return self.match.player2

    def __str__(self):
        return '{}-{}'.format(self.player1_points, self.player2_points)


class Match(models.Model):
    date = models.DateField(default=datetime.now)
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_set')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_set')

    def winner(self):
        "The user that won more sets in the game"
        counter = collections.Counter([s.winner() for s in self.sets.all()])
        if counter:
            # TODO should consider invalid/pending matches?
            return max(counter, key=counter.get)
        else:
            return None

    def __str__(self):
        sets = [str(s) for s in self.sets.all()]
        sets = ' / '.join(sets)
        return '{} vs {}: {}'.format(self.player1, self.player2, sets)

    class Meta:
        verbose_name_plural = 'matches'
