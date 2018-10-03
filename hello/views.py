import os
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse

from password_required.decorators import password_required

from monzo.monzo import Monzo
from monzo.errors import BadRequestError, UnauthorizedError

from .models import Greeting


@password_required
def activate_webhook(request):
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    account_id = client.get_first_account()['id']
    webhook_url = request.build_absolute_uri('webhook/' + account_id)
    client.register_webhook(webhook_url=webhook_url, account_id=account_id)
    print(client.get_webhooks(account_id))
    return redirect('index')

@password_required
def deactivate_webhook(request):
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    account_id = client.get_first_account()['id']
    webhook_id = client.get_first_webhook(account_id)['id']
    client.delete_webhook(webhook_id)
    return redirect('index')

def webhook(request, account_id):
    if request.method == 'POST':
        greeting = Greeting()
        greeting.save()
        print(request.body)
        return HttpResponse('Received. Thanks Monzo!')
    else:
        return HttpResponse(status=405)

@password_required
def index(request):
    app_name = request.build_absolute_uri().split('.')[0][8:]
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))

    try:
        account_id = client.get_first_account()['id']
        webhooks = client.get_webhooks(account_id)['webhooks']
        print(webhooks)
        webhook_active = bool(webhooks)

        ACCOUNT_TYPES = {
            'uk_retail': 'Personal',
            'uk_retail_joint': 'Joint'
        }
        accounts = client.get_accounts()['accounts']
        num_accounts = len(client.get_accounts()['accounts'])
    except (BadRequestError, UnauthorizedError):
        return render(request, 'invalid-token.html', {'app_name': app_name })

    """
    for i, acc in enumerate(accounts):
    txns = client.get_transactions(acc['id'])['transactions']
 
             #tag_coffee(txns)
 
             #with open(str(i) + '.json', 'w') as f:
             #    f.write(json.dumps(txns, sort_keys=True, indent=4))
    """

    context = {
        'num_accounts': num_accounts,
        'webhook_active': webhook_active
    }
    return render(request, 'index.html', context)


@password_required
def db(request):
    """Show received events from webhook."""
    greetings = Greeting.objects.all()
    return render(request, 'db.html', {'greetings': greetings})

