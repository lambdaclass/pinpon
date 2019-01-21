import pinpon.models as models

def current():
    "Return the latest version of the player ranking"
    # all players start with 10 points
    players = models.Player.objects.all()
    counter = {p: 10 for p in players}

    matches = models.Match.objects.all()
    for match in matches:
        winner = match.winner()
        if winner:
            loser = match.player2 if winner is match.player1 else match.player1
            # we add half of the loser points to the winner
            counter[winner] += counter[loser] // 2

    mapping = points2rank(counter)
    ranking = {}
    for player, points in counter.items():
        ranking[player] = {"rank": mapping[points], "points": points}

    return ranking

def rank(ranking, player):
    """
    Return the current ranking and points of the given user.
    Users with the same amount of points will have the same ranking.
    """
    rank = ranking[player]
    return rank["rank"], rank["points"]

def export(ranking):
    entries = sorted(ranking.items(), key=lambda r: r[1]["rank"])
    return [(r[1]["rank"], r[0], r[1]["points"]) for r in entries]

## helper functions

def points2rank(counter):
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
