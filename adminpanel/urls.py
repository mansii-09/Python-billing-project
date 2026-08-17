from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("organisations/", views.organisations_page, name="organisations"),
    path("organisation/add/", views.add_organisation, name="add_organisation"),
    path("organisation/update/<int:id>/", views.update_organisation, name="update_organisation"),
    path("organisation/delete/<int:id>/", views.delete_organisation, name="delete_organisation"),
    path("customers/", views.customers_page, name="customers"),
    path("customer/add/", views.add_customer, name="add_customer"),
    path("customer/update/<int:id>/", views.update_customer, name="update_customer"),
    path("customer/delete/<int:id>/", views.delete_customer, name="admin_delete_customer"),
    path("invoices/", views.invoices_page, name="invoices"),
    path("invoice/add/", views.add_invoice, name="add_invoice"),
    path("invoice/update/<int:id>/", views.update_invoice, name="update_invoice"),
    path("invoice/delete/<int:id>/", views.delete_invoice, name="delete_invoice"),
    path("aproducts/", views.products_page, name="aproducts"),
    path("product/add/", views.add_product, name="add_product"),
    path("product/update/<int:id>/", views.update_product, name="update_product"),
    path("product/delete/<int:id>/", views.delete_product, name="delete_product"),
    path("employees_page/", views.employees_page, name="employees_page"),
    path("employee/add/", views.add_employee, name="admin_add_employee"),
    path("employee/update/<int:id>/", views.update_employee, name="update_employee"),
    path("employee/delete/<int:id>/", views.delete_employee, name="admin_delete_employee"),
    ]
