'''
# 作者: 112122858 黃涴淨
# 描述: 用於計算貸款的每月還款金額。
'''
import pandas as pd

def gen_amortization_schedule(loan_amount, annual_interest_rate, loan_term_years, monthly_payment):
    """
    生成貸款每月還款表

    參數：
    loan_amount (float): 貸款金額
    annual_interest_rate (float): 年利率（百分比）
    loan_term_years (int): 貸款期限（年）

    返回：
    DataFrame: 包含期數、未償還貸款、償還本金、支付利息和供款的表格
    """

    # 年利率轉換成月利率
    monthly_interest_rate = annual_interest_rate / 12 / 100
    # 貸款期限轉換成月數
    loan_term_months = loan_term_years * 12

    schedule = []

    remaining_balance = loan_amount

    for period in range(1, loan_term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append([
            period,
            round(remaining_balance, 2),
            round(principal_payment, 2),
            round(interest_payment, 2),
            round(monthly_payment, 2)
        ])

    df = pd.DataFrame(schedule, columns=['期數', '未償還貸款', '償還本金', '支付利息', '供款'])
    df['未償還貸款'] = df['未償還貸款'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')
    df['償還本金'] = df['償還本金'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')
    df['支付利息'] = df['支付利息'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')
    df['供款'] = df['供款'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')
    return df

def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years):
    """
    計算每月還款金額

    參數：
    loan_amount (float): 貸款金額
    annual_interest_rate (float): 年利率（百分比）
    loan_term_years (int): 貸款期限（年）

    返回：
    str: 每月還款金額，格式化為字串
    """
    # 年利率轉換成月利率
    monthly_interest_rate = annual_interest_rate / 12 / 100
    # 貸款期限轉換成月數
    loan_term_months = loan_term_years * 12
    # 計算每月還款金額
    if monthly_interest_rate == 0:  # 若利率為0，則直接平均分攤
        monthly_payment = loan_amount / loan_term_months
    else:
        numerator = monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months
        denominator = (1 + monthly_interest_rate) ** loan_term_months - 1
        monthly_payment = loan_amount * numerator / denominator

     # 計算總利息
    total_payment = monthly_payment * loan_term_months
    total_interest = total_payment - loan_amount

    df = gen_amortization_schedule(
        loan_amount,
        annual_interest_rate,
        loan_term_years,
        monthly_payment
        )
    table_html = df[['期數', '未償還貸款', '償還本金', '支付利息', '供款']].to_html(
            escape=False, render_links=True, classes='table table-striped', index=False)

    th_style = """
    <style>
        th, td { text-align: center; }
        td:nth-child(1) { text-align: right; }
        td:nth-child(2) { text-align: right; }
        td:nth-child(3) { text-align: right; }
        td:nth-child(4) { text-align: right; }
        td:nth-child(5) { text-align: right; }
    </style>
    """

    # 加入 Bootstrap 樣式與列印按鈕
    bs_link = "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"

    result = (
        f'<p>每月還款金額 : {int(monthly_payment):,}</p>'
        f'<p>總利息 : {int(total_interest):,}</p>'
        f'<p>還款總金額 : {int(total_payment):,}</p>'
        '<p><p>貸款每月還款表</p>'
        f"<link href=\"{bs_link}\" rel=\"stylesheet\">{th_style}{table_html}"
    )
    return result
