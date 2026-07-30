from django.urls import path
from .views import (
    AnalyticsDashboardView,
    ChartDataAPIView,
    AIInsightsView,
    ReportPageView,
    ExportReportView
)

urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('api/chart-data/', ChartDataAPIView.as_view(), name='chart_data_api'),
    path('ai-insights/', AIInsightsView.as_view(), name='ai_insights'),
    path('reports/', ReportPageView.as_view(), name='report_page'),
    path('reports/export/', ExportReportView.as_view(), name='export_report'),
]
