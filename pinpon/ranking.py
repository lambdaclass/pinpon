import pinpon.models as models

class BaseRankingStrategy():
    def __init__(self):
        players = models.Player.objects.all()
        counter = {p: 100 for p in players}

        matches = models.Match.objects.all()
        for match in matches:
            winner = match.winner()
            if winner:
                loser = match.player2 if winner is match.player1 else match.player1
                counter[winner] += int(self.get_winner_points(counter, winner, loser))
                counter[loser] += int(self.get_loser_points(counter, winner, loser))

        mapping = self._points2rank(counter)
        ranking = {}
        for player, points in counter.items():
            ranking[player] = {"rank": mapping[points], "points": points}

        self.ranking = ranking

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
    def get_winner_points(self, counter, winner, loser):
        # we add half of the loser points to the winner
        return counter[loser] // 2

    def get_loser_points(self, counter, winner, loser):
        return 0

class EloRankingStrategy(BaseRankingStrategy):
    # The maximum possible adjustment per game set at K = 16 for masters and K = 32 for weaker players.
    def get_winner_points(self, counter, winner, loser):
        points_winner = counter[winner]
        points_loser = counter[loser]
        return self._k_factor(points_winner) * (1 - self._expectation(points_winner, points_loser))

    def get_loser_points(self, counter, winner, loser):
        points_winner = counter[winner]
        points_loser = counter[loser]
        return - self._k_factor(points_winner) * self._expectation(points_winner, points_loser)

    def _expectation(self, points1, points2):
        return 1 / (1 + 10 ** ((points1 - points2) / 400))

    def _k_factor(self, points):
        if points <= 100:
            return 32
        elif points <= 200:
            return 24
        else:
            return 16
