import os
import json
import datetime
import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages

from password_required.decorators import password_required

from monzo.monzo import Monzo
from monzo.errors import BadRequestError, UnauthorizedError

from .forms import TagForm
from .models import Webhook, Tag, Settings



ACCOUNT_TYPES = {
  'uk_prepaid': 'Prepaid',
  'uk_retail': 'Personal',
  'uk_retail_joint': 'Joint'
}

strftime_code = {
    'Weekday': "%A",
    'Weekday Short': "%a",
    'Month': "%B",
    'Month Short': "%B",
    'Week no.': "week%W",
    'Year': "%Y"
}

@password_required
def activate_webhook(request, account_id):

    webhook, created = Webhook.objects.get_or_create(id=account_id)
    webhook.enabled = True
    webhook.save()

    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    webhook_url = request.build_absolute_uri('webhook/' + account_id)
    client.register_webhook(webhook_url=webhook_url, account_id=account_id)

    print(client.get_webhooks(account_id))
    
    return redirect('index')

@password_required
def deactivate_webhook(request, account_id):
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    webhook_id = client.get_first_webhook(account_id)['id']
    client.delete_webhook(webhook_id)

    webhook = Webhook.objects.get(id=account_id)
    webhook.enabled = False
    webhook.save()

    return redirect('index')

def webhook(request, account_id):
    if request.method == 'POST':
        print(request.body)
        return HttpResponse('Transaction event received. Thanks Monzo!')
    else:
        return HttpResponse(status=405)

@password_required
def account(request, account_id):
    app_name = request.build_absolute_uri().split('.')[0][8:]
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    try:
        settings = Settings.objects.filter()[0]
        settings.last_used_account = account_id
        settings.save()
    except:
        Settings.objects.create(last_used_account=account_id)

    try:
        webhooks = client.get_webhooks(account_id)['webhooks']
        print(webhooks)
        webhook_active = bool(webhooks)

        accounts = client.get_accounts()['accounts']
        print(accounts)

        tags = Tag.objects.all()

    except (BadRequestError, UnauthorizedError):
        return render(request, 'invalid-token.html', {'app_name': app_name })

    context = {
        'app_name': app_name,
        'accounts': accounts,
        'account_id': account_id,
        'tags': tags,
        'webhook_active': webhook_active,
        'strftime_codes': strftime_code
    }
    return render(request, 'account.html', context)

@password_required
def index(request):
    app_name = request.build_absolute_uri().split('.')[0][8:]
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))

    try:
        account = client.get_first_account()
        if account['closed']:
            account_id = client.get_accounts()['accounts'][1]['id']
        else:
            account_id = account['id']
    except (BadRequestError, UnauthorizedError):
        return render(request, 'invalid-token.html', {'app_name': app_name })

    return redirect('account', account_id)

@password_required
def tag_new(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            settings = Settings.objects.filter()[0]
            return redirect('account', settings.last_used_account)
    else:
        form = TagForm()
    app_name = request.build_absolute_uri().split('.')[0][8:]
    return render(request, 'tag-edit.html', {'form': form})

@password_required
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            tag = form.save()
            settings = Settings.objects.filter()[0]
            return redirect('account', settings.last_used_account)
    else:
        form = TagForm(instance=tag)
    app_name = request.build_absolute_uri().split('.')[0][8:]
    return render(request, 'tag-edit.html', {'form': form})

@password_required
def tag_apply(request, pk, account_id):
    """Tag transactions using the Monzo API."""
    tag = get_object_or_404(Tag, pk=pk)
    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    txns = client.get_transactions(account_id)['transactions']
    txns = parse_datetimes(txns)
    
    txns_updated = 0
    for txn in txns:
        try:
            if eval(tag.expression):
                if tag.label not in txn['notes']:
                    updated_txn = client.update_transaction_notes(
                                    txn['id'],
                                    txn['notes'] + ' ' + tag.label
                                  ) 
                    txns_updated += 1
        except (TypeError, KeyError):
            pass
        except Exception as e:
            raise e
            messages.warning(request, 'There is a problem with your Python expression: ' + str(e))
            return redirect('account', account_id)

    if txns_updated:
        messages.info(request, '{} transactions tagged. Android users may need to delete App Cache and Data before changes are visible in the app.'.format(txns_updated))
    else:
        messages.warning(request, 'No transactions match the given criteria')
    return redirect('account', account_id)


def parse_datetimes(transactions):
    """
    Convert timestamp strings into datetime objects.
    This function is pretty ugly.
    It's because timestamps can have between 0 and 3 digits of millisecond precision.
    """
    for txn in transactions:
        for (key, value) in txn.items():
            try:
                mlsec = value[-4:-1]
                txn[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.{}Z".format(mlsec))
            except:
                try:
                    mlsec = value[-3:-1]
                    txn[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.{}Z".format(mlsec))
                except:
                    try:
                        mlsec = value[-2:-1]
                        txn[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.{}Z".format(mlsec))
                    except:
                        try:
                            txn[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                        except:
                            if key in ('created', 'updated'):
                                raise
                            if key == 'settled' and value == '':
                                pass
    return transactions


@password_required
def delete_all_tags(request, account_id):
    """TODO"""
    messages.info(request, 'Coming soon...')
    return redirect('account', account_id)

@password_required
def show_all_tags(request, account_id):
    """TODO"""
    messages.info(request, 'Coming soon...')
    return redirect('account', account_id)


@password_required
def tag_by_time(request, account_id, time_period):
    """Tag all transactions according to time period."""

    client = Monzo(os.environ.get('MONZO_ACCESS_TOKEN'))
    txns = client.get_transactions(account_id)['transactions']
    txns = parse_datetimes(txns)
    
    txns_updated = 0
    for txn in txns:
        tag = '#{}'.format(txn['created'].strftime(strftime_code[time_period]).lower())
        if tag not in txn['notes']:
            updated_txn = client.update_transaction_notes(
                            txn['id'],
                            txn['notes'] + ' ' + tag
                          ) 
            txns_updated += 1

    messages.info(request, 'All {} transactions were tagged. Android users may need to delete App Cache and App Data before changes are visible in the app.'.format(txns_updated))

    return redirect('account', account_id)

