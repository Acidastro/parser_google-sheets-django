from django.db import models


class ParserListModel(models.Model):
    N = models.IntegerField(db_column='№', blank=True, null=True)
    order_N = models.CharField(db_column='заказ №', max_length=50, blank=True, null=True)
    price_dol = models.CharField(db_column='стоимость,$', max_length=50, blank=True, null=True)
    date = models.CharField(db_column='срок поставки', max_length=50, blank=True, null=True)
    price_rub = models.CharField(db_column='стоимость в руб.', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test777'

    def __str__(self):
        return f'{ self.order_N, self.price_rub}'
