from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from minors.models import DirectCost
from contracts.models import Contract
from openpyxl import Workbook
import time

# 可重用的列名索引
columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U']


# 将数据库中所有数据对象的内容写入到Excel格式的合同台账中的功能
# 主函数getCompleteList, 辅助函数writeHeader和writeContent
@login_required
def getCompleteList(request):
    # 文件名称为当天合同台账
    filename = time.strftime("%Y-%m-%d", time.localtime()) + " contract.xlsx"

    # 创建excel文件
    result = Workbook()

    # 查找所有的合同
    contracts = Contract.objects.all().order_by('company', 'subject', 'index')

    # 调用函数来向活动工作表中写入表头
    writeHeader(result)

    # 写入数据
    writeContent(contracts, result)

    # 虚拟保存后通过响应返回该文件
    response = HttpResponse(content=save_virtual_workbook(result),
                            content_type='application/octet-stream')

    filenameString = 'attachment;filename={}'.format(filename)
    response['Content-Disposition'] = filenameString

    return response


def writeHeader(workbook: Workbook):
    # 设置活动工作表名称

    worksheet = workbook.active

    worksheet.title = '合同台账'

    # 向第一行写入表头信息, 需要哪些要好好考虑一下, 一共写几个也是问题关键

    # 01 公司
    # 02 合同类型
    # 03 合同索引
    # 04 供应商名称
    # 05 合同金额
    # 06 决算金额
    # 07 累计付款金额
    # 08 未付金额
    # 09 发票金额
    # 10 增值税额
    # 11 付款比例
    # 12 应付合计
    # 13 预付合计
    # 14 开发成本
    # 15 签订时间
    # 16 印花税类型
    # 17 印花税税率
    # 18 印花税金额
    # 19 是否有效
    # 20 是否计入成本
    # 21 合同摘要

    worksheet['A1'].value = '公司'
    worksheet['B1'].value = '合同类型'
    worksheet['C1'].value = '合同索引'
    worksheet['D1'].value = '供应商名称'
    worksheet['E1'].value = '合同金额'
    worksheet['F1'].value = '决算金额'
    worksheet['G1'].value = '累计付款金额'
    worksheet['H1'].value = '未付金额'
    worksheet['I1'].value = '发票金额'
    worksheet['J1'].value = '增值税额'
    worksheet['K1'].value = '付款比例'
    worksheet['L1'].value = '应付合计'
    worksheet['M1'].value = '预付合计'
    worksheet['N1'].value = '开发成本'
    worksheet['O1'].value = '签订时间'
    worksheet['P1'].value = '印花税类型'
    worksheet['Q1'].value = '印花税税率'
    worksheet['R1'].value = '印花税金额'
    worksheet['S1'].value = '是否有效'
    worksheet['T1'].value = '是否计入成本'
    worksheet['U1'].value = '合同摘要'


def writeContent(contracts, workbook: Workbook):
    # 对于contracts中的每个合同, 写入其中的内容

    worksheet = workbook.active

    # 获取计数看看, 实际用不到该代码
    # count = contracts.count()

    # print("合同总数量是: {}".format(count))

    # 初始从第二行开始写入
    start = 2

    for contract in contracts:
        worksheet[columns[0] + str(start)].value = contract.company.name
        worksheet[columns[1] + str(start)].value = contract.subject.name
        worksheet[columns[2] + str(start)].value = contract.index
        worksheet[columns[3] + str(start)].value = contract.supplier
        worksheet[columns[4] + str(start)].value = contract.amount
        worksheet[columns[5] + str(start)].value = contract.definite
        worksheet[columns[6] + str(start)].value = contract.total_payment()
        worksheet[columns[7] + str(start)].value = contract.remaining_payment()
        worksheet[columns[8] + str(start)].value = contract.total_requisition()
        worksheet[columns[9] + str(start)].value = contract.total_tax()
        worksheet[columns[10] + str(start)].value = contract.payment_rate()
        worksheet[columns[11] + str(start)].value = contract.total_payable
        worksheet[columns[12] + str(start)].value = contract.total_prepaid
        worksheet[columns[13] + str(start)].value = contract.development_cost
        worksheet[columns[14] + str(start)].value = contract.sign
        worksheet[columns[15] + str(start)].value = contract.stamp.name
        worksheet[columns[16] + str(start)].value = contract.stamp.rate
        worksheet[columns[17] + str(start)].value = contract.stamp_amount

        if contract.active:
            worksheet[columns[18] + str(start)].value = '是'
        else:
            worksheet[columns[18] + str(start)].value = '否'

        if contract.is_cost:
            worksheet[columns[19] + str(start)].value = '是'
        else:
            worksheet[columns[19] + str(start)].value = '否'

        worksheet[columns[20] + str(start)].value = contract.text
        start = start + 1


# 配套生成非合同付款的代码, 主函数getMinorsList, 辅助函数writeMinorHeader和writeMinorContent
@login_required
def getMinorsList(request):
    # 文件名称中加上当天时间
    filename = time.strftime("%Y-%m-%d", time.localtime()) + " minors.xlsx"

    # 创建excel文件
    result = Workbook()

    # 查找所有的非合同付款
    direct_costs = DirectCost.objects.all().order_by('company', 'subject')

    # 调用函数来向活动工作表中写入表头
    writeMinorHeader(result)

    # 写入数据
    writeMinorContent(direct_costs, result)

    # 虚拟保存后通过响应返回该文件
    response = HttpResponse(content=save_virtual_workbook(result),
                            content_type='application/octet-stream;charset=utf-8')
    filenamestring = 'attachment;filename={}'.format(filename)
    response['Content-Disposition'] = filenamestring

    return response


def writeMinorHeader(workbook: Workbook):
    # 设置活动工作表名称

    worksheet = workbook.active

    worksheet.title = '非合同付款台账'

    # 向第一行写入表头信息, 需要哪些要好好考虑一下, 一共写几个也是问题关键

    # 01 公司
    # 02 类别
    # 03 内容
    # 04 供应商名称
    # 05 金额
    # 06 请款金额
    # 07 付款金额
    # 08 增值税额
    # 09 开发成本
    # 10 备注

    worksheet['A1'].value = '公司'
    worksheet['B1'].value = '类别'
    worksheet['C1'].value = '内容'
    worksheet['D1'].value = '供应商名称'
    worksheet['E1'].value = '金额'
    worksheet['F1'].value = '请款金额'
    worksheet['G1'].value = '付款金额'
    worksheet['H1'].value = '增值税额'
    worksheet['I1'].value = '开发成本'
    worksheet['J1'].value = '备注'


def writeMinorContent(costs, workbook: Workbook):

    worksheet = workbook.active

    # 获取计数看看, 实际用不到该代码

    # 初始从第二行开始写入
    start = 2

    for contract in costs:
        worksheet[columns[0] + str(start)].value = contract.company.name
        worksheet[columns[1] + str(start)].value = contract.subject.name
        worksheet[columns[2] + str(start)].value = contract.name
        worksheet[columns[3] + str(start)].value = contract.supplier
        worksheet[columns[4] + str(start)].value = contract.amount
        worksheet[columns[5] + str(start)].value = contract.total_reqs
        worksheet[columns[6] + str(start)].value = contract.total_pays
        worksheet[columns[7] + str(start)].value = contract.total_tax
        worksheet[columns[8] + str(start)].value = contract.total_cost
        worksheet[columns[9] + str(start)].value = contract.text
        start = start + 1
