import inspect

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not (inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not (m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices


class TradeTypes(ChoiceEnum):
    Market = 0
    Limit = 1


class SideTypes(ChoiceEnum):
    Buy = 0
    Sell = 1


class CurrencyTypes(ChoiceEnum):
    USD = 0
    BTC = 1


class BaseModel(models.Model):
    """Abstract base model that all other models should inherit from."""
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    modified_at = models.DateTimeField('Modified at', auto_now=True)

    class Meta:
        abstract = True
        app_label = "exchange"
        verbose_name = _('BaseModel')
        verbose_name_plural = _('BaseModels')


class User(User):
    pass


# bitcoins will be represented directly as satoshis, as per the bitcoin protocol
class Order(BaseModel):
    order_type = models.CharField(max_length=1, choices=TradeTypes.choices())
    side = models.CharField(max_length=1, choices=SideTypes.choices())
    amount = models.DecimalField(max_digits=100000000000000,
                                 decimal_places=2)  # max digits are one million bitcoins times 10^8 to translate to satoshis
    limit = models.DecimalField(max_digits=1000000000000,
                                decimal_places=2)  # max digits is one ten thousand bitcoins times 10^8 to translate to satoshis
    from_currency = models.CharField(max_length=3, choices=CurrencyTypes.choices())
    to_currency = models.CharField(max_length=3,
                                   choices=CurrencyTypes.choices())  # it should not be possible for the from currency to equal the to currency


# these are generated by exchanges
class Trade(BaseModel):
    # the amount each unit from the buy_order will cost, expressed in terms of the sell currency
    rate = models.DecimalField(max_digits=10000000000,
                               decimal_places=2)  # max_digits is 10^8 to convert to satoshis times 100 to account for decimal places
    buy_order = models.ForeignKey('Order', related_name="buy_order")
    sell_order = models.ForeignKey('Order', related_name="sell_order")
    filled = models.BooleanField(default=False)


# url where the exchange can be contacted, and base currency that the exchange uses
class Exchange(BaseModel):
    api_url = models.CharField(max_length=255)
    base_currency = models.CharField(max_length=3, choices=CurrencyTypes.choices())


#security supported by exchange
class ExchangeSecurity(BaseModel):
    exchange = models.ForeignKey('Exchange')
    currency_type = models.CharField(max_length=3, choices=CurrencyTypes.choices())


class Account(BaseModel):
    user = models.ForeignKey('User')
    currency_type = models.CharField(max_length=3, choices=CurrencyTypes.choices())
    balance = models.DecimalField(max_digits=100000000000000, decimal_places=2)