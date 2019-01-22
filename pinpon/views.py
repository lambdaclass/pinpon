from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pinpon.ranking as ranking
import pinpon.head2head as head2head
import pinpon.models as models

@csrf_exempt
def slack_command(request):
    "Called to handle slack slash commands."
    SLACK_COMMANDS = {
        "rank": ranking_command,
        "ranking": ranking_command,
        "h2h": h2h_command,
        "head2head": h2h_command
    }

    args = request.POST["text"].split()
    name, args = args[0], args[1:]
    command = SLACK_COMMANDS.get(name, error_command)
    response_text = command(args)

    return JsonResponse({"response_type": "in_channel", "text": response_text})

def ranking_command(args):
    current = ranking.current()
    data = ranking.export(current)
    return "\n".join(map(format_ranking, data))

def format_ranking(data):
    rank = data[0]
    emoji = data[1].slack_emoji
    name = data[1].name
    points = data[2]
    return "#{} :{}: {} ({} pts)".format(rank, emoji, name, points)

def h2h_command(args):
    player1_alias, player2_alias = args
    player1 = models.Player.objects.by_alias(player1_alias)
    player2 = models.Player.objects.by_alias(player2_alias)

    ranks = ranking.current()
    p1_rank, _ = ranking.rank(ranks, player1)
    p2_rank, _ = ranking.rank(ranks, player2)
    h2h = head2head.get(player1, player2)
    return "#{} :{}: VS #{} :{}:\n{} ({}%) WINS {} ({}%)\n{} ({}%) POINTS {} ({}%)".format(
        p1_rank, player1.slack_emoji, p2_rank, player2.slack_emoji,
        h2h[player1]["wins"], h2h[player1]["wins%"],
        h2h[player2]["wins"], h2h[player2]["wins%"],
        h2h[player1]["points"], h2h[player1]["points%"],
        h2h[player2]["points"], h2h[player2]["points%"],
    )

def error_command(args):
    return "Sorry, I don't understand that command."
