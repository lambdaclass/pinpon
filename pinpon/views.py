import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pinpon.head2head as head2head
import pinpon.models as models
from pinpon.ranking import EloRankingStrategy

@csrf_exempt
def slack_command(request):
    "Called to handle slack slash commands."

    args = request.POST["text"].split()
    name, args = args[0], args[1:]
    command = SLACK_COMMANDS.get(name, error_command)
    response_text = command(args)

    return JsonResponse({"response_type": "in_channel", "text": response_text})

def ranking_command(args):
    """
    `/pinpon rank`
    Prints the player rankings.
    """
    ranking = EloRankingStrategy()
    data = ranking.export()
    return "\n".join(map(format_ranking, data))

def format_ranking(data):
    rank = data[0]
    emoji = data[1].slack_emoji
    name = data[1].name
    points = data[2]
    return "#{} :{}: {} ({} pts)".format(rank, emoji, name, points)

def save_command(args):
    """
    `/pinpon save turco manu 11-4/5-11/14-12`
    `/pinpon save turco manu`
    Saves a match between the given players.
    """
    today = datetime.datetime.today()
    player1_alias = args[0]
    player2_alias = args[1]
    player1 = models.Player.objects.by_alias(player1_alias)
    player2 = models.Player.objects.by_alias(player2_alias)

    match = models.Match.objects.create(player1=player1, player2=player2, date=today)

    if len(args) > 2:
        sets = args[2].split('/')
        for s in sets:
            player1_points, player2_points = map(int, s.split('-'))
            models.Set.objects.create(match=match, player1_points=player1_points, player2_points=player2_points)
    else:
        models.Set.objects.create(match=match, player1_points=21, player2_points=1)

    return "Done!"

def elo_command(args):
    """
    `/pinpon elo turco manu`
    Returns the ELO prediction of the outcome of a game.
    """
    player1_alias, player2_alias = args
    player1 = models.Player.objects.by_alias(player1_alias)
    player2 = models.Player.objects.by_alias(player2_alias)

    elo = EloRankingStrategy()
    p1_points = elo.points(player1)
    p2_points = elo.points(player2)

    probability = elo._expectation(p1_points, p2_points)
    winner_points = elo.get_winner_points(p1_points, p2_points) - p1_points
    loss_points = elo.get_loser_points(p2_points, p1_points) - p1_points

    return "P(win) = {:.2f}\nwin points: +{}\nloss points: {}".format(probability,
                                                                      round(winner_points),
                                                                      round(loss_points))

def h2h_command(args):
    """
    `/pinpon h2h turco manu`
    Returns the head2head of the given players.
    """
    player1_alias, player2_alias = args
    player1 = models.Player.objects.by_alias(player1_alias)
    player2 = models.Player.objects.by_alias(player2_alias)

    ranking = EloRankingStrategy()
    p1_rank = ranking.rank(player1)
    p2_rank = ranking.rank(player2)
    h2h = head2head.get(player1, player2)
    return "#{} :{}: VS #{} :{}:\n{} ({}%) WINS {} ({}%)".format(
        p1_rank, player1.slack_emoji, p2_rank, player2.slack_emoji,
        h2h[player1]["wins"], h2h[player1]["wins%"],
        h2h[player2]["wins"], h2h[player2]["wins%"],
    )

def help_command(args):
    """
    `/pinpon help`
    Prints this help message.
    """
    docs = [cmd.__doc__ for cmd in SLACK_COMMANDS.values()]
    return "".join(docs)


def error_command(args):
    return "Sorry, I don't understand that command."

SLACK_COMMANDS = {
    "rank": ranking_command,
    "h2h": h2h_command,
    "save": save_command,
    "elo": elo_command,
    "help": help_command
}
