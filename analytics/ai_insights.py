import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from django.utils import timezone
from tracker.models import Expense, Income, Budget, Category
from django.db.models import Sum

def get_ai_insights(user):
    insights = {
        'forecast': None,
        'anomalies': [],
        'budget_risks': [],
        'recommendations': [],
        'has_enough_data': False
    }

    # Fetch User Data
    expenses = Expense.objects.filter(user=user)
    incomes = Income.objects.filter(user=user)

    if not expenses.exists() or expenses.count() < 5:
        # Not enough data for meaningful machine learning models
        insights['recommendations'].append(
            "Welcome! Once you log at least 5 expenses, our AI engine will generate spending forecasts, anomalous transaction flags, and budget warnings."
        )
        return insights

    insights['has_enough_data'] = True

    # Convert expenses to Pandas DataFrame
    exp_data = [{
        'id': e.id,
        'amount': float(e.amount),
        'date': pd.to_datetime(e.date),
        'category': e.category.name,
        'description': e.description or 'No description'
    } for e in expenses]
    df_exp = pd.DataFrame(exp_data)

    # 1. EXPENSE FORECASTING (Linear Regression)
    try:
        # Group by Month-Year
        df_monthly = df_exp.groupby(df_exp['date'].dt.to_period('M'))['amount'].sum().reset_index()
        # Sort chronologically
        df_monthly = df_monthly.sort_values('date')
        
        num_months = len(df_monthly)
        if num_months >= 2:
            # Prepare data for regression
            X = np.arange(num_months).reshape(-1, 1) # 0, 1, 2...
            y = df_monthly['amount'].values

            model = LinearRegression()
            model.fit(X, y)

            # Predict next month (month index: num_months)
            next_month_idx = np.array([[num_months]])
            forecast_amount = max(0.0, float(model.predict(next_month_idx)[0]))

            # Category specific forecasts
            category_forecasts = {}
            for cat in df_exp['category'].unique():
                df_cat = df_exp[df_exp['category'] == cat]
                df_cat_monthly = df_cat.groupby(df_cat['date'].dt.to_period('M'))['amount'].sum().reset_index()
                
                # Fill missing months with 0
                all_months = df_monthly['date']
                df_cat_monthly = df_cat_monthly.set_index('date').reindex(all_months, fill_value=0).reset_index()
                
                model_cat = LinearRegression()
                model_cat.fit(X, df_cat_monthly['amount'].values)
                cat_forecast = max(0.0, float(model_cat.predict(next_month_idx)[0]))
                if cat_forecast > 0:
                    category_forecasts[cat] = round(cat_forecast, 2)

            insights['forecast'] = {
                'total': round(forecast_amount, 2),
                'categories': category_forecasts,
                'trend': 'rising' if model.coef_[0] > 0 else 'falling'
            }
        else:
            # Basic fallback
            insights['forecast'] = {
                'total': round(df_monthly['amount'].mean(), 2),
                'categories': {},
                'trend': 'stable (insufficient history for trend analysis)'
            }
    except Exception as e:
        insights['forecast'] = None

    # 2. ANOMALY DETECTION (Z-Score on transaction size)
    try:
        amounts = df_exp['amount']
        mean_amt = amounts.mean()
        std_amt = amounts.std()

        # If standard deviation is non-zero, flag items with Z-score > 2
        if std_amt > 0:
            df_exp['z_score'] = (df_exp['amount'] - mean_amt) / std_amt
            anomalous_df = df_exp[df_exp['z_score'] > 2]
            for _, row in anomalous_df.iterrows():
                insights['anomalies'].append({
                    'id': int(row['id']),
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'category': row['category'],
                    'amount': row['amount'],
                    'description': row['description'],
                    'reason': f"Unusually high purchase size (Z-score: {row['z_score']:.2f})"
                })
    except Exception as e:
        pass

    # 3. BUDGET RISK ANALYSIS (Spending Velocity)
    try:
        today = timezone.now().date()
        active_budgets = Budget.objects.filter(
            user=user, start_date__lte=today, end_date__gte=today
        )

        for budget in active_budgets:
            total_days = (budget.end_date - budget.start_date).days + 1
            days_elapsed = (today - budget.start_date).days + 1

            if days_elapsed > 0:
                current_spending = float(budget.current_spending)
                daily_burn_rate = current_spending / days_elapsed
                
                # Extrapolate to end of budget period
                projected_total = daily_burn_rate * total_days
                budget_amt = float(budget.amount)

                if projected_total > budget_amt:
                    risk_percent = int(((projected_total - budget_amt) / budget_amt) * 100)
                    insights['budget_risks'].append({
                        'category': budget.category.name,
                        'budget_amount': budget_amt,
                        'current_spending': current_spending,
                        'projected_spending': round(projected_total, 2),
                        'days_left': total_days - days_elapsed,
                        'risk_level': 'High' if risk_percent > 20 else 'Medium',
                        'message': f"Based on spending velocity, you are projected to exceed your budget for {budget.category.name} by {risk_percent}%."
                    })
    except Exception as e:
        pass

    # 4. SMART RECOMMENDATIONS & SAVINGS ADVISORY
    try:
        # A. High Expense Alert
        df_cat_sums = df_exp.groupby('category')['amount'].sum()
        top_cat = df_cat_sums.idxmax()
        top_cat_percentage = int((df_cat_sums.max() / df_cat_sums.sum()) * 100)
        
        if top_cat_percentage > 35:
            insights['recommendations'].append(
                f"Your spending is highly concentrated in **{top_cat}** ({top_cat_percentage}% of total expenses). Try implementing a budget here to distribute your funds better."
            )

        # B. Saving vs Income Advisory
        total_monthly_expense = float(df_exp[df_exp['date'].dt.month == today.month]['amount'].sum())
        
        monthly_incomes = incomes.filter(date__month=today.month, date__year=today.year)
        total_monthly_income = float(monthly_incomes.aggregate(total=Sum('amount'))['total'] or 0)

        if total_monthly_income > 0:
            savings_rate = ((total_monthly_income - total_monthly_expense) / total_monthly_income) * 100
            target_rate = 20.0 # Standard rule of thumb
            
            if user.monthly_savings_target > 0:
                target_rate = float((user.monthly_savings_target / total_monthly_income) * 100)

            if savings_rate < target_rate:
                insights['recommendations'].append(
                    f"Your current month savings rate is {savings_rate:.1f}%, which is below your target of {target_rate:.1f}%. Consider cutting discretionary spending in non-essential categories."
                )
            else:
                insights['recommendations'].append(
                    f"Congratulations! You saved {savings_rate:.1f}% of your income this month, exceeding your target rate of {target_rate:.1f}%."
                )
        
        # C. Anomaly Flag warning in advisory
        if len(insights['anomalies']) > 0:
            insights['recommendations'].append(
                f"We detected {len(insights['anomalies'])} unusually high transactions recently. Review your expense log for any unexpected or one-off charges."
            )

    except Exception as e:
        pass

    return insights
