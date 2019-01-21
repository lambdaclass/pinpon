import pinpon.models as models

def get(player1, player2):
    matches = models.Match.objects.head2head(player1, player2)
    wins = {player1: 0, player2: 0}
    points = {player1: 0, player2: 0}

    for match in matches:
        wins[match.winner()] += 1
        match_points = match.player_points()
        points[match.player1] += match_points[0]
        points[match.player2] += match_points[1]

    total_points = points[player1] + points[player2]
    return {player1: {"wins": wins[player1],
                      "points": points[player1],
                      "wins%": percentage(matches.count(), wins[player1]),
                      "points%": percentage(total_points, points[player1])},
            player2: {"wins": wins[player2],
                      "points": points[player2],
                      "wins%": percentage(matches.count(), wins[player2]),
                      "points%": percentage(total_points, points[player2])}}

def percentage(total, singular):
    return int((singular * 100) / total)
