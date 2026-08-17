
from django.urls import path
# from .views import OrganisationView,LoginView,index,CustomerView,CustomerFormView,delete,edit,update,logout,invoicePage,InvoiceView
from .views import *
from organisation import views

urlpatterns = [
    path('',views.LoginView, name='login'),
    path('signup/',OrganisationView,name = 'signup'),
    
    path('index/',index, name = 'index'),
    
    path('customer/',customer,name = 'customer'),
    path('delete_customer/<int:id>/', delete_customer, name='delete_customer'),
    path('customer_update/<int:id>/', customer_update, name='customer_update'),
    path('add_customer/',addcustomer, name = 'addcustomer'),
    path('invoiceview/',invoiceview, name = 'invoiceview'),
    path('invoicepage/',InvoicePage,name='invopage'),
    path('invoiceform/',invoiceform,name='invoiceform'),
    path('invoiceUpdate/',InvoiceUpdate,name='InvoUp'),
    path('productview/',ProductView,name = 'productview'),
    path('productform/',productform,name='productform'),
    path('detailpage/',DetailPage,name='detailpage'),
    path('logout/',logout,name = "logout"),
    path('all_invoices/',Total_Invoice_Page,name='total_invoice_page'),
    path('employees/', employees, name='employees'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('delete_employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('edit_employee/<int:id>/', views.edit_employee, name='edit_employee'),
    path('send-payment-email/',views.send_payment_email,name="send_payment_email"),
    # QR upload
    path('upload-qr/', views.upload_qr, name='upload_qr'),

    # share qr
    path('share-qr/', views.share_qr, name='share_qr'),

    
    
    path('invoice/view/<int:id>/', views.view_invoice, name='view_invoice'),
    path('invoice/pdf/<int:id>/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('products/', views.product_list, name='product_list'),
    
    path('product/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:id>/', views.delete_product, name='org_delete_product'),
    
    path('customer/history/<int:id>/', views.customer_history, name='customer_history'),
    path('category/', views.category_list, name='category_list'),
    path('category/delete/<int:id>/', views.delete_category, name='delete_category'),
   path('reports/', views.reports_view, name='reports'),
   path('settings/', views.settings_view, name='settings'),
]