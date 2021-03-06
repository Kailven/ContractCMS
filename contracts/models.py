from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=40, verbose_name='部门名称')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created', ]
        verbose_name = '部门'
        verbose_name_plural = '部门'



class Company(models.Model):
    name = models.CharField(max_length=40, verbose_name='公司名称')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created', ]
        verbose_name = '公司'
        verbose_name_plural = '公司'


class Subject(models.Model):
    code = models.CharField(max_length=1, verbose_name='种类代码')
    name = models.CharField(max_length=20, verbose_name='种类名称')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return "{} {}".format(self.code, self.name)

    @property
    def tag(self):
        return self.code

    @property
    def full_name(self):
        return "{}-{}".format(self.code, self.name)

    class Meta:
        ordering = ['created', ]
        verbose_name = '合同种类'
        verbose_name_plural = '合同种类'


class Stamp(models.Model):
    name = models.CharField(max_length=20, verbose_name='印花税类型', unique=True)
    rate = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='印花税税率')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created', ]
        verbose_name = '印花税'
        verbose_name_plural = '印花税'


class Contract(models.Model):
    index = models.CharField(max_length=50, verbose_name='索引')
    name = models.CharField(max_length=50, verbose_name='合同名称', db_index=True)
    supplier = models.CharField(max_length=50, verbose_name='供应商名称', db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contracts', verbose_name='公司',
                                default=1)
    subject = models.ForeignKey(Subject, related_name='contracts', on_delete=models.CASCADE, verbose_name='合同类别')
    sign = models.DateField(verbose_name='签订时间')
    amount = models.DecimalField(max_digits=16, decimal_places=2, verbose_name='初始金额')
    definite = models.DecimalField(max_digits=16, decimal_places=2, verbose_name='决算金额', blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name='有效')
    is_cost = models.BooleanField(default=True, verbose_name='是否进成本')
    jgc = models.BooleanField(default=False, verbose_name='甲供材')
    text = models.TextField(blank=True, null=True, verbose_name='合同条款摘要')
    master = models.PositiveIntegerField(null=True, blank=True, verbose_name='补充合同')
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='contracts', verbose_name='印花税类型',
                              default=12)
    stamp_amount = models.DecimalField(max_digits=16, decimal_places=2, verbose_name='印花税金额', default=0)
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间', db_index=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    department = models.ForeignKey(Department, on_delete=models.CASCADE,related_name='dep',verbose_name='部门名称', default=1)



    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contracts:contract_detail', args=[self.id])

    def hassupple(self):
        supple = Contract.objects.filter(master=self.id).count()
        return supple != 0

    def is_supple(self):
        return True if self.master else False

    def master_contract(self):
        if self.is_supple():
            return get_object_or_404(Contract, id=int(self.master))
        else:
            return None

    def supple_contracts(self):
        if self.hassupple():
            return Contract.objects.filter(master=self.id)
        return None

    # 总发票金额
    def total_requisition(self):
        if self.requisitions.all().count():
            reqs = self.requisitions.all().aggregate(Sum('invoice'))['invoice__sum']
            return reqs
        else:
            return 0

    # 付款比例
    def requisition_rate(self):
        if self.definite and self.total_requisition():
            return self.total_requisition() / self.definite
        elif self.amount and self.total_requisition():
            return self.total_requisition() / self.amount
        else:
            return None

    # 总付款金额
    def total_payment(self):
        if self.payments.all().count():
            return self.payments.all().aggregate(Sum('amount'))['amount__sum']
        else:
            return 0

    # 总付款比例
    def payment_rate(self):
        if self.total_payment() and self.definite:
            return self.total_payment() / self.definite
        elif self.total_payment() and self.amount:
            return self.total_payment() / self.amount
        else:
            return None

    # 总已经收到发票的税金
    def total_tax(self):
        if self.payments.all().count():
            return self.payments.all().aggregate(Sum('tax'))['tax__sum']
        return 0

    # 总发票-税金 = 总无税金额, 即按照发票口径的开发成本
    def total_cost(self):
        if self.payments.all().count():
            return self.total_payment() - self.total_tax()
        return 0

    # 剩余应付
    def remaining_payment(self):
        if self.total_payment() and self.definite:
            return self.definite - self.total_payment()

        elif self.total_payment() and self.amount:
            return self.amount - self.total_payment()

        else:
            return 0

    # 1.3版本新增 统计总的应付, 预付, 和通过付款金额计算出开发成本

    # 预付合计数 = 手工录入, 不允许收到票的预付存在. 每次填写支付的时候填写
    @property
    def total_prepaid(self):
        if self.payments.all().count():
            return self.payments.all().aggregate(Sum('prepaid'))['prepaid__sum']
        return 0

    # 应付合计数 = 手工填写付款中的每次应付账款合计数
    @property
    def total_payable(self):
        if self.payments.all().count():
            return self.payments.all().aggregate(Sum('payable'))['payable__sum']
        return 0

    # 开发成本 由于过程中如果只录入发票金额, 但是还没有录入应付或者预付, 则结果就不正确, 所以必须使用总金额法
    @property
    def development_cost(self):
        return self.total_payment() - self.total_prepaid+ self.total_payable - self.total_tax()

    class Meta:
        ordering = ('subject', 'index', 'created')
        verbose_name = '合同'
        verbose_name_plural = '合同'
