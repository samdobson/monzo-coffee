# Standard lib
import re
import os
import json
import datetime
from collections import Counter

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

# Third-party Django
from password_required.decorators import password_required

# Third party
from monzo.monzo import Monzo
from monzo.auth import MonzoOAuth2Client
from monzo.errors import BadRequestError, UnauthorizedError
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError

# Django app
from .forms import TagForm
from .models import Webhook, Tag, Settings, History


ACCOUNT_TYPES = {
  'uk_prepaid': 'Prepaid',
  'uk_retail': 'Personal',
  'uk_retail_joint': 'Joint'
}

strftime_code = {
    'Weekday': "%A",
    'Weekday Short': "%a",
    'Month': "%B",
    'Month Short': "%b",
    'Week no.': "week%W",
    'Year': "%Y"
}

@password_required
def transactions(request):
    """Endpoint for serving transaction data to json-viewer React App"""
    client = init_client()
    account_id = client.get_first_account()['id']
    transactions = client.get_transactions(account_id)['transactions']
    return JsonResponse(transactions)

@password_required
def json_viewer(request):
    return render(request, 'json-viewer.html')

@password_required
def start_auth(request):
    oauth_client = MonzoOAuth2Client(
            os.environ.get('MONZO_CLIENT_ID'),
            os.environ.get('MONZO_CLIENT_SECRET'),
            redirect_uri=request.build_absolute_uri('auth-redirect'),
            refresh_callback=save_token_to_db
    )
    return redirect(oauth_client.authorize_token_url()[0])

@password_required
def auth_redirect(request):
    code = request.GET.get('code', None) 
    #state = request.GET.get('state', None) 
    if code:
        try:
            oauth_client = MonzoOAuth2Client(
                    os.environ.get('MONZO_CLIENT_ID'),
                    os.environ.get('MONZO_CLIENT_SECRET'),
                    redirect_uri=request.build_absolute_uri('auth-redirect'),
                    refresh_callback=save_token_to_db
            )
            oauth_client.fetch_access_token(code)
        except InvalidClientIdError as e:
            if 'Authorization code has expired' in repr(e):
                return HttpResponse('The authorization code has expired. Please try again.')
    return redirect('index')

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
    client = init_client()

    try:
        userdata = Settings.objects.filter()[0]
        userdata.last_used_account = account_id
        userdata.save()
    except:
        Settings.objects.create(last_used_account=account_id)

    try:
        webhooks = client.get_webhooks(account_id)['webhooks']
        webhook_active = bool(webhooks)

        accounts = client.get_accounts()['accounts']
        custom_tags = Tag.objects.all()

    except (BadRequestError, UnauthorizedError):
        return render(request, 'invalid-token.html', {'app_name': app_name })

    transactions = client.get_transactions(account_id)['transactions']

    notes = ' '.join([value for txn in transactions 
                        for (key, value) in txn.items() if key == 'notes']
                    )
    tags = re.findall(r"(#\w+)", notes)
    tag_counts = dict(Counter(tags))

    suggestions = ['#suggestion{}'.format(i + 1) for i in range(20)]
    txn_count = len(transactions)

    ### CHARTS
    # Online vs. in-store
    online = 0
    for txn in transactions:
        try:
            if txn['merchant']['online']:
                online += 1
        except (KeyError, AttributeError, TypeError):
            continue

    in_store = txn_count - online

    # UK vs. abroad
    uk = 0
    for txn in transactions:
        try:
            if txn['merchant']['address']['country'] == 'GBR':
                uk += 1
        except (KeyError, AttributeError, TypeError):
            continue

    abroad = txn_count - uk

    # Prettify account names
    for acc in accounts:
        acc['type'] = ACCOUNT_TYPES[acc['type']]

    context = {
        'app_name': app_name,
        'accounts': accounts,
        'account_id': account_id,
        'webhook_active': webhook_active,
        'strftime_codes': strftime_code,
        'custom_tags': custom_tags,
        'tag_counts': tag_counts,
        'suggestions': suggestions,
        'txn_count' : len(transactions),
        'tags_used_count' : sum(tag_counts.values()),
        'history' : History.objects.all(),
        'online_data' : { 'online': online, 'in_store': in_store },
        'uk_data' : { 'uk': uk, 'abroad': abroad }
    }
    return render(request, 'account.html', context)

@password_required
def index(request):
    userdata = Settings.objects.all()
    if len(userdata):
        userdata = Settings.objects.filter()[0]
        if not userdata.token:
            return render(request, 'index.html')
        else:
            print(userdata.token)

            client = init_client()
            account = client.get_first_account()
            if account['closed']:
                account_id = client.get_accounts()['accounts'][1]['id']
            else:
                account_id = account['id']
            userdata.last_used_account = account_id
            userdata.save()
            return redirect('account', account_id)
    else:
        return render(request, 'index.html')


@password_required
def tag_new(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            userdata = Settings.objects.filter()[0]
            return redirect('account', userdata.last_used_account)
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
            userdata = Settings.objects.filter()[0]
            return redirect('account', userdata.last_used_account)
    else:
        form = TagForm(instance=tag)
    app_name = request.build_absolute_uri().split('.')[0][8:]
    return render(request, 'tag-edit.html', {'form': form})

@password_required
def tag_apply(request, pk, account_id):
    """Tag transactions using the Monzo API."""
    tag = get_object_or_404(Tag, pk=pk)
    client = init_client()
    txns = client.get_transactions(account_id)['transactions']
    txns = parse_datetimes(txns)
    
    txn_ids = []
    for txn in txns:
        try:
            if eval(tag.expression):
                if tag.label not in txn['notes']:
                    updated_txn = client.update_transaction_notes(
                                    txn['id'],
                                    txn['notes'] + ' ' + tag.label
                                  ) 
                    txn_ids.append(txn['id'])
        except (TypeError, KeyError):
            continue
        except Exception as e:
            raise e
            messages.warning(request, 'There is a problem with your Python expression: ' + str(e))
            return redirect('account', account_id)

    txns_updated = len(txn_ids)
    if txns_updated:
        History.objects.create(
            tag=tag.label,
            txn_ids='|'.join(txn_ids),
            txns_affected=len(txn_ids)
        )
        messages.info(request, '{} transactions tagged. You may need to delete App Cache and Data before updates are visible in the Monzo app.'.format(txns_updated))
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
def tag_by_time(request, account_id, time_period):
    """Tag all transactions according to time period."""

    client = init_client()
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

    messages.info(request, 'All {} transactions were tagged. You may need to delete App Cache and App Data before changes are visible in the Monzo app.'.format(txns_updated))

    return redirect('account', account_id)

@password_required
def tag_test(request, account_id):
    """Tag most recent transaction with #test"""
    client = init_client()
    txns = client.get_transactions(account_id)['transactions']
    txns = parse_datetimes(txns)
    txn = max(txns, key=lambda x: x['created'])

    if '#test' not in txn['notes']:
        updated_txn = client.update_transaction_notes(
                                    txn['id'],
                                    txn['notes'] + ' #test'
                                  ) 
        History.objects.create(
            account_id=account_id,
            action='tag_apply',
            tag='#test',
            txn_ids=txn['id'],
            txns_affected=1
        )
        messages.info(request, 'Your most recent transaction was tagged with #test. If it is older than a week, may need to delete App Cache and Data before the update is visible in the Monzo app.')

    return redirect('account', account_id)

@password_required
def undo_action(request, pk, account_id):
    """Undo an action performed previously"""
    client = init_client()
    txns = client.get_transactions(account_id)['transactions']

### TODO: Move below to utils.py
def save_token_to_db(token):
    try:
        userdata = Settings.objects.filter()[0]
    except:
        userdata, created = Settings.objects.create()
    userdata.token = json.dumps(token, sort_keys=True, indent=4)
    userdata.save()

def init_client():
    userdata = Settings.objects.filter()[0]
    token = json.loads(userdata.token)
    oauth_client = MonzoOAuth2Client(
                         os.environ.get('MONZO_CLIENT_ID'),
                         os.environ.get('MONZO_CLIENT_SECRET'),
                         access_token=token['access_token'],
                         refresh_token=token['refresh_token'],
                         expires_at=token['expires_at'],
                         refresh_callback=save_token_to_db)
    return Monzo.from_oauth_session(oauth_client)

