from .models import Account


def accounts(request):
    accounts = Account.objects.filter(is_superadmin=False)
    return dict(account=accounts)


