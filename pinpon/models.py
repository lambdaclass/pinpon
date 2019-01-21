import collections
from datetime import datetime

from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=150, blank=False)
    aliases = models.CharField(max_length=200, blank=True)
    email = models.EmailField('email address')
    is_active = models.BooleanField('active', default=True)
    slack_username = models.CharField(max_length=30)
    slack_emoji = models.CharField(max_length=30)

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


class Match(models.Model):
    date = models.DateField(default=datetime.now)
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_set')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_set')

    # the rank/points of the players before the match
    # (may be useful for scoring algorithms based on ranking)
    player1_rank = models.PositiveSmallIntegerField()
    player2_rank = models.PositiveSmallIntegerField()
    player1_points = models.PositiveIntegerField()
    player2_points = models.PositiveIntegerField()

    def winner(self):
        "The user that won more sets in the game"
        counter = collections.Counter([s.winner() for s in self.sets.all()])
        if counter:
            return max(counter, key=counter.get)
        else:
            return None

    def __str__(self):
        # FIXME add set results
        # FIXME add player rankings
        return '{} vs {}'.format(self.player1, self.player2)

    class Meta:
        verbose_name_plural = 'matches'
