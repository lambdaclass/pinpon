from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pinpon.ranking as ranking

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
    username = data[1].slack_username
    points = data[2]
    return "#{} :{}: @{} ({} pts)".format(rank, emoji, username, points)

def h2h_command(args):
    # TODO
    return "Not implemented yet."

def error_command(args):
    return "Sorry, I don't understand that command."
