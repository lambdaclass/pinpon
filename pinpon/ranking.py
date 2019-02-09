import datetime
import pinpon.models as models

class BaseRankingStrategy():
    def __init__(self):
        players = models.Player.objects.all()
        counter = {p: self.default_points() for p in players}

        three_months_ago = datetime.datetime.today() - datetime.timedelta(days=90)
        matches = models.Match.objects.filter(date__gte=three_months_ago)
        for match in matches:
            winner = match.winner()
            if winner:
                loser = match.player2 if winner is match.player1 else match.player1
                points_winner = self.get_winner_points(counter[winner], counter[loser])
                points_loser = self.get_loser_points(counter[winner], counter[loser])

                counter[winner] = self._clean_points(points_winner)
                counter[loser] = self._clean_points(points_loser)

        mapping = self._points2rank(counter)
        ranking = {}
        for player, points in counter.items():
            ranking[player] = {"rank": mapping[points], "points": points}

        self.ranking = ranking

    def _clean_points(self, points):
        # don't allow points below 1
        return max(1, round(points))

    def _points2rank(self, counter):
        """
        Given a point counter dict return a mapping from points to rank index,
        with shared indexes for ties.
        """
        points = sorted(counter.values(), reverse=True)
        mapping = {}
        rank = 1
        for p in points:
            if p not in mapping:
                mapping[p] = rank
            rank += 1
        return mapping

    def rank(self, player):
        """
        Return the current ranking of the given player.
        Players with the same amount of points will have the same ranking.
        """
        rank = self.ranking[player]
        return rank["rank"]

    def points(self, player):
        """
        Return the current amount of points of the given player.
        """
        rank = self.ranking[player]
        return rank["points"]

    def export(self):
        entries = sorted(self.ranking.items(), key=lambda r: r[1]["rank"])
        return [(r[1]["rank"], r[0], r[1]["points"]) for r in entries]


class LoloRankingStrategy(BaseRankingStrategy):
    def default_points(self):
        return 100

    def get_winner_points(self, points_winner, points_loser):
        # we add half of the loser points to the winner
        return points_winner + points_loser // 2

    def get_loser_points(self, _points_winner, _points_loser):
        return 0


class EloRankingStrategy(BaseRankingStrategy):
    def default_points(self):
        return 2000

    def get_winner_points(self, points_winner, points_loser):
        return points_winner + self._k_factor(points_winner) * self._expectation(points_loser, points_winner)

    def get_loser_points(self, points_winner, points_loser):
        return points_loser - self._k_factor(points_winner) * self._expectation(points_loser, points_winner)

    def _expectation(self, points1, points2):
        return 1 / (1 + 10 ** ((points2 - points1) / 400))

    def _k_factor(self, points):
        """
        The maximum possible adjustment per game set at K = 16 for masters and
        K = 32 for weaker players.
        """
        if points < 2000:
            return 32
        elif points < 2100:
            return 24
        else:
            return 16
