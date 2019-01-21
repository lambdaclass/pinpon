import collections
from datetime import datetime

from django.db import models
from django.db.models import Q

class PlayerManager(models.Manager):
    def by_alias(self, alias):
        query = (Q(slack_username=alias[1:]) |
                 Q(aliases__contains=alias) |
                 Q(name=alias))
        return super().get_queryset().filter(query).first()

class Player(models.Model):
    objects = PlayerManager()

    name = models.CharField(max_length=150, blank=False)
    aliases = models.CharField(max_length=200, blank=True)
    email = models.EmailField('email address')
    is_active = models.BooleanField('active', default=True)
    slack_username = models.CharField(max_length=30, blank=True)
    slack_emoji = models.CharField(max_length=30, blank=True)

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

class MatchManager(models.Manager):
    def head2head(self, player1, player2):
        "Return a QuerySet of matches between the given players."
        query = Q(player1=player1, player2=player2) | Q(player1=player2, player2=player1)
        return super().get_queryset().filter(query)

class Match(models.Model):
    objects = MatchManager()

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

    def player_points(self):
        p1, p2 = 0, 0
        for s in self.sets.all():
            p1 += s.player1_points
            p2 += s.player2_points
        return p1, p2

    def __str__(self):
        sets = [str(s) for s in self.sets.all()]
        sets = ' / '.join(sets)
        return '{} vs {}: {}'.format(self.player1, self.player2, sets)

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ('date',)
