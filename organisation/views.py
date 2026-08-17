from email.mime.image import MIMEImage
from urllib import request
from django.contrib import messages
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from .models import InvoiceItem, OrganisationDetails,CustomerDetails,Invoice_Details,Product,Employee
from .forms import OrganisationForm,CustomerForm,Invoice_Details_Form,Product_Form
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


def OrganisationView(request):

    if request.method == "POST":

        form = OrganisationForm(request.POST)

        if form.is_valid():

            org = form.save()

            # create a corresponding Django auth user so we can use authenticate/login
            try:
                # use the provided user_id as username and email field for authentication
                if not User.objects.filter(username=org.user_id).exists():
                    User.objects.create_user(
                        username=org.user_id,
                        email=org.email,
                        password=org.password_1
                    )
            except Exception:
                # ignore failures (e.g. duplicate) to keep signup working
                pass

            # auto login after signup
            request.session['org_id'] = org.id
            request.session['company_name'] = org.company_name

            return redirect('index')   

    else:
        form = OrganisationForm()

    return render(request, 'signup.html', {
        'org': form
    })


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import OrganisationDetails

def LoginView(request):
    if request.method == "POST":
        identifier = request.POST.get("email")
        password = request.POST.get("password")
        admin_login = request.POST.get("admin_login")

        # ---------- ADMIN LOGIN ----------
        if admin_login:
            user = authenticate(request, username=identifier, password=password)
            if user and user.is_superuser:
                login(request, user)
                return redirect("admin_dashboard")
            else:
                return render(request, "registration/login.html", {"error": "Invalid admin username or password"})

        # ---------- USER LOGIN ----------
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                if hasattr(user_obj, 'organisationdetails'):
                    request.session['org_id'] = user_obj.organisationdetails.id
                    request.session['company_name'] = user_obj.organisationdetails.company_name
                return redirect("index")
        except User.DoesNotExist:
            pass

        # fallback login using OrganisationDetails
        try:
            org = OrganisationDetails.objects.get(email=identifier, password_1=password)
            request.session['org_id'] = org.id
            request.session['company_name'] = org.company_name
            return redirect("index")
        except OrganisationDetails.DoesNotExist:
            return render(request, "registration/login.html", {"error": "Invalid email or password"})

    return render(request, "registration/login.html")




from django.shortcuts import render, redirect
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

def index(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')
    company = request.session.get('company_name')

    # =========================
    # COUNTS
    # =========================
    customer_count = CustomerDetails.objects.filter(companyName=org_id).count()

    # =========================
    # DATE
    # =========================
    today = datetime.today()

    # =========================
    # TOTAL SALES (MONTH)
    # =========================
    total_sales = Invoice_Details.objects.filter(
        companyName=org_id,
        Date__month=today.month,
        Date__year=today.year
    ).aggregate(total=Sum('final_total'))['total'] or 0

    # =========================
    # TODAY SALES
    # =========================
    today_sales = Invoice_Details.objects.filter(
        companyName=org_id,
        Date=today.date()
    ).aggregate(total=Sum('final_total'))['total'] or 0

    # =========================
    # TOP PRODUCT (SAFE)
    # =========================
    top_product_obj = Product.objects.filter(
        companyName=org_id
    ).order_by('-stock').first()

    top_product = top_product_obj.Product_name if top_product_obj else "N/A"

    # =========================
    # SALARY
    # =========================
    total_salary = Employee.objects.filter(
        companyName=org_id
    ).aggregate(total=Sum('salary'))['total'] or 0

    # =========================
    # PROFIT / LOSS
    # =========================
    revenue = total_sales - total_salary
    revenue_status = "profit" if revenue >= 0 else "loss"

    # =========================
    # SALES CHART (MONTHLY)
    # =========================
    labels = []
    sales_values = []

    for i in range(11, -1, -1):
        dt = today - relativedelta(months=i)

        labels.append(dt.strftime("%b"))

        month_total = Invoice_Details.objects.filter(
            companyName=org_id,
            Date__year=dt.year,
            Date__month=dt.month
        ).aggregate(total=Sum('final_total'))['total'] or 0

        sales_values.append(month_total)

    # =========================
    # INVOICE CHART (COUNT)
    # =========================
    invoice_labels = []
    invoice_values = []

    for i in range(11, -1, -1):
        dt = today - relativedelta(months=i)

        invoice_labels.append(dt.strftime("%b"))

        inv_count = Invoice_Details.objects.filter(
            companyName=org_id,
            Date__year=dt.year,
            Date__month=dt.month
        ).count()

        invoice_values.append(inv_count)

    # =========================
    # RECENT INVOICES
    # =========================
    recent_invoices = Invoice_Details.objects.filter(
        companyName=org_id
    ).order_by('-Date')[:5]

    # =========================
    # CONTEXT
    # =========================
    context = {
        'company': company,
        'customer_count': customer_count,

        'total_sales': total_sales,
        'today_sales': today_sales,
        'top_product': top_product,

        'total_salary': total_salary,
        'revenue': abs(revenue),
        'revenue_status': revenue_status,

        'recent_invoices': recent_invoices,

        # charts
        'sales_labels': json.dumps(labels),
        'sales_data': json.dumps(sales_values),

        'invoice_labels': json.dumps(invoice_labels),
        'invoice_data': json.dumps(invoice_values),
    }

    return render(request, 'index.html', context)

def logout(request):
    request.session.flush()
    return redirect('login')
    
# Customer Data ---------------
   
def customer(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    customers = CustomerDetails.objects.filter(
        companyName=org_id
    ).order_by('-id')

    return render(request,'customer.html',{
        'customers':customers
    })
    
    

def addcustomer(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')
    organisation = OrganisationDetails.objects.get(id=org_id)

    data = {}

    if request.method == "POST":

        cust_name = request.POST.get('cust_name')
        cont_person = request.POST.get('cont_person')
        contact_num = request.POST.get('contact_num')
        email = request.POST.get('email')
        company_type = request.POST.get('company_type')
        address = request.POST.get('address')
        address_2 = request.POST.get('address_2')
        landmark = request.POST.get('landmark')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        CustomerDetails.objects.create(

            companyName = organisation,

            cust_name = cust_name,
            cont_person = cont_person,
            contact_num = contact_num,
            email = email,
            company_type = company_type,

            address = address,
            address_2 = address_2,
            landmark = landmark,

            country = country,
            state = state,
            city = city,

            pincode = pincode

        )
        messages.success(request, "Customer added successfully")
        return redirect('customer')


    return render(request,'addcustomer.html',{
        'data':data
    })


def customer_update(request, id):

    if not request.session.get('org_id'):
        return redirect('login')

    customer = CustomerDetails.objects.get(id=id)

    if request.method == "POST":

        customer.cust_name = request.POST.get('cust_name')
        customer.cont_person = request.POST.get('cont_person')
        customer.contact_num = request.POST.get('contact_num')
        customer.email = request.POST.get('email')
        customer.company_type = request.POST.get('company_type')

        customer.address = request.POST.get('address')
        customer.address_2 = request.POST.get('address_2')
        customer.landmark = request.POST.get('landmark')

        customer.country = request.POST.get('country')
        customer.state = request.POST.get('state')
        customer.city = request.POST.get('city')

        customer.pincode = request.POST.get('pincode')

        customer.save()

        messages.success(request, "Customer updated successfully")

        return redirect('customer')

    return render(request,'customerUpdate.html',{
        'customer':customer
    })

def delete_customer(request, id):

    if not request.session.get('org_id'):
        return redirect('login')

    customer = CustomerDetails.objects.get(id=id)
    customer.delete()

    messages.success(request, "Customer deleted successfully")

    return redirect('customer')

# Invoice Data ---------------

def Total_Invoice_Page(request):
    return render(request,'Total_Invoice_Page.html')


def invoiceview(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    invoices = Invoice_Details.objects.filter(companyName=org_id).order_by('-id')

    return render(request, 'invoiceview.html', {
        'data': invoices
    })
   
def InvoicePage(request):
    return render(request,'invoice_list.html')
    
    
    
def DetailPage(request):
    return render(request,'DetailPage.html')


from datetime import datetime


from django.contrib import messages   # 🔥 important

def invoiceform(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    customers = CustomerDetails.objects.filter(companyName=org_id)
    products = Product.objects.filter(companyName=org_id)

    if request.method == "POST":

        customer = CustomerDetails.objects.get(id=request.POST.get('customer'))
        product = Product.objects.get(id=request.POST.get('product'))

        qty = int(request.POST.get('Qty') or 0)

        # 🚨 STOCK CHECK
        if product.stock < qty:
            messages.error(request, "Not enough stock ❌")
            return redirect('invoiceform')

        # ✅ CREATE INVOICE
        invoice = Invoice_Details.objects.create(
            companyName_id=org_id,
            Cust_name=customer,
            Invoice_type="Regular",
            Dispatch_through="",
            Due_date=datetime.today(),
            Bank="",
            Payment_type="",
            Payment_note="",
            T_c="",
            Document_note=""
        )

        # ✅ CREATE ITEM
        item = InvoiceItem.objects.create(
            Invoice=invoice,
            product=product,
            Qty=qty,
            Price=product.Price
        )

        # ✅ REDUCE STOCK
        product.stock -= qty
        product.save()

        # ✅ UPDATE TOTAL
        invoice.subtotal = item.Total
        invoice.final_total = item.Total
        invoice.save()

        # 🔥 SUCCESS MESSAGE
        messages.success(request, "Invoice generated successfully ✅")

        return redirect('invoiceview')

    return render(request, 'invoiceform.html', {
        'customers': customers,
        'products': products
    })
    
def InvoiceUpdate(request):
        return render(request,'invoiceform.html')


def ProductView(request):
    return render(request,'temp_product.html')


from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Invoice_Details, Product, CustomerDetails,Category


def productform(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    categories = Category.objects.all() 

    if request.method == "POST":

        Product.objects.create(
            
            companyName_id=org_id,
            category_id=request.POST.get('category'), 
            Product_name=request.POST.get('Product_name'),
            Hsn_code=request.POST.get('Hsn_code') or '',
            Price=float(request.POST.get('Price') or 0),
            Discount=int(request.POST.get('Discount') or 0),
            Cgst=int(request.POST.get('Cgst') or 0),
            Sgst=int(request.POST.get('Sgst') or 0),
            Igst=int(request.POST.get('Igst') or 0),
            Cess=int(request.POST.get('Cess') or 0),
            stock=int(request.POST.get('stock') or 0)
        )
        messages.success(request, "Product added successfully")

        return redirect('product_list')

    return render(request, 'productform.html', {
            'categories': categories,
         })
    
def ProductUpdate(request):
    return render(request,'productform.html')


from .models import Employee
from django.shortcuts import render, redirect


def employees(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    employees = Employee.objects.filter(companyName=org_id)

    return render(request,'employees.html',{
        'employees':employees
    })


def add_employee(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    if request.method == "POST":

        Employee.objects.create(

            companyName_id = org_id,

            name = request.POST.get('name'),
            email = request.POST.get('email'),
            phone = request.POST.get('phone'),
            role = request.POST.get('role'),
            salary = request.POST.get('salary'),
            joining_date = request.POST.get('joining_date'),

        )

        messages.success(request, "Employee added successfully")

        return redirect('employees')

    return render(request,'add_employee.html')

def edit_employee(request,id):

    emp = get_object_or_404(Employee,id=id)

    if request.method == "POST":

        emp.name = request.POST.get('name')
        emp.email = request.POST.get('email')
        emp.phone = request.POST.get('phone')
        emp.role = request.POST.get('role')
        emp.salary = request.POST.get('salary')
        emp.joining_date = request.POST.get('joining_date')

        emp.save()

        messages.success(request, "Employee updated successfully")
        return redirect('employees')

    return render(request,'edit_employee.html',{
        'emp':emp
    })



def delete_employee(request,id):

    emp = Employee.objects.get(id=id)
    emp.delete()

    messages.success(request, "Employee deleted successfully")
    return redirect('employees')


import qrcode
import base64
from io import BytesIO

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect
from .models import CustomerDetails


def send_payment_email(request):

    customers = CustomerDetails.objects.all()

    payment_link = request.build_absolute_uri('/pay/')

    # Generate QR Code
    qr = qrcode.make(payment_link)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    for c in customers:

        html_content = render_to_string('payment_email.html',{
            'customer':c,
            'payment_link':payment_link,
            'qr_code':qr_base64
        })

        email = EmailMultiAlternatives(
            subject="Payment Link",
            body="Scan QR or click link to pay",
            to=[c.email]
        )

        email.attach_alternative(html_content,"text/html")

        email.send()

    return redirect('customer')



from .forms import PaymentQRForm
from .models import PaymentQR,CustomerDetails


def upload_qr(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    # get previously uploaded QR
    qr = PaymentQR.objects.filter(companyName=org_id).order_by('-id').first()

    if request.method == "POST":

        payment_link = request.POST.get("payment_link")
        qr_image = request.FILES.get("qr_image")

        if qr:  # update existing

            if payment_link:
                qr.payment_link = payment_link

            if qr_image:
                qr.qr_image = qr_image

            qr.save()

        else:  # create first QR

            PaymentQR.objects.create(
                companyName_id=org_id,
                payment_link=payment_link,
                qr_image=qr_image
            )

        return redirect("share_qr")

    return render(request,"upload_qr.html",{
        "qr":qr
    })


def share_qr(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    customers = CustomerDetails.objects.filter(companyName=org_id)

    qr = PaymentQR.objects.filter(companyName=org_id).order_by('-id').first()

    if not qr:
        messages.error(request,"Please upload payment QR first.")
        return redirect("upload_qr")

    if request.method == "POST":

        selected = request.POST.getlist("customers")

        selected_customers = CustomerDetails.objects.filter(id__in=selected)

        for c in selected_customers:

            html_content = render_to_string(
                "payment_email.html",
                {
                    "customer": c,
                    "qr": qr
                }
            )

            email = EmailMultiAlternatives(
                subject="Payment Request",
                body="Scan QR to pay",
                to=[c.email]
            )

            email.attach_alternative(html_content,"text/html")

            with open(qr.qr_image.path,"rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID","<qr_code>")
                img.add_header("Content-Disposition","inline",filename="qr.png")
                email.attach(img)

            email.send()

        messages.success(request,"Payment emails sent successfully!")

        return redirect("customer")

    return render(request,"share_qr.html",{
        "customers":customers,
        "qr":qr
    })
    
    
from django.db.models import Sum

def update_invoice_total(invoice_id):

    products = Product.objects.filter(Invoice_id=invoice_id)

    subtotal = sum([p.Qty * p.Price for p in products])
    gst_total = sum([((p.Cgst + p.Sgst + p.Igst) * (p.Qty * p.Price)) / 100 for p in products])
    discount_total = sum([(p.Qty * p.Price * p.Discount) / 100 for p in products])

    final_total = subtotal + gst_total - discount_total

    invoice = Invoice_Details.objects.get(id=invoice_id)
    invoice.subtotal = subtotal
    invoice.gst_total = gst_total
    invoice.discount_total = discount_total
    invoice.final_total = final_total
    invoice.save()
    
    
    
from django.shortcuts import get_object_or_404

def view_invoice(request, id):

    # ✅ GET INVOICE (NOT CUSTOMER)
    invoice = get_object_or_404(Invoice_Details, id=id)

    # ✅ GET ITEMS (CORRECT MODEL)
    items = InvoiceItem.objects.filter(Invoice=invoice)

    return render(request, 'view_invoice.html', {
        'invoice': invoice,
        'items': items
    })
    
    
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Invoice_Details, InvoiceItem



def download_invoice_pdf(request, id):

    # GET INVOICE
    invoice = get_object_or_404(Invoice_Details, id=id)
    customer = invoice.Cust_name

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.Invoice_num}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # CUSTOM STYLES
    title_style = ParagraphStyle(
        'TitleCenter',
        parent=styles['Title'],
        alignment=1
    )

    invoice_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading2'],
        textColor=colors.HexColor("#4f7cff")
    )

    # ================= COMPANY HEADER =================

    elements.append(Paragraph("Billing Pro", title_style))
    elements.append(Paragraph("Invoice Management System", styles['Normal']))
    elements.append(Paragraph("Ahmedabad, India", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ================= INVOICE TITLE =================
    elements.append(Paragraph("INVOICE", invoice_style))
    elements.append(Spacer(1, 15))

    # ================= CUSTOMER INFO =================
    elements.append(Paragraph(f"<b>Customer:</b> {customer.cust_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Invoice No:</b> {invoice.Invoice_num}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {invoice.Date}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ================= TABLE =================
    data = [["Product", "Qty", "Price", "Total"]]

    items = InvoiceItem.objects.filter(Invoice=invoice)

    for item in items:
        data.append([
            item.product.Product_name,
            item.Qty,
            f"Rs. {item.Price}",
            f"Rs. {round(item.Total, 2)}"
        ])

    table = Table(data, colWidths=[200, 60, 100, 100])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f7cff")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    # ================= TOTAL =================
    elements.append(Paragraph(f"Subtotal: Rs. {invoice.subtotal}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Final Total: Rs. {invoice.final_total}</b>", styles['Heading2']))
    elements.append(Spacer(1, 30))

    # ================= FOOTER =================
    elements.append(Paragraph("Thank you for your business!", styles['Italic']))
    elements.append(Paragraph("Generated by Billing Pro System", styles['Normal']))

    doc.build(elements)

    return response


    
def product_list(request):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    products = Product.objects.filter(companyName=org_id)

    return render(request, 'product_list.html', {
        'products': products
    })
    
    
    
def create_invoice(request):

    if request.method == "POST":

        customer = CustomerDetails.objects.get(id=request.POST.get('customer'))
        product = Product.objects.get(id=request.POST.get('product'))

        qty = int(request.POST.get('Qty'))

        # 🚨 STOCK CHECK
        if product.stock < qty:
            return HttpResponse("❌ Not enough stock")

        # ✅ CREATE INVOICE
        invoice = Invoice_Details.objects.create(
            companyName_id=request.session.get('org_id'),
            Cust_name=customer,
            Invoice_type="Regular",
            Dispatch_through="",
            Due_date=datetime.today(),
            Bank="",
            Payment_type="",
            Payment_note="",
            T_c="",
            Document_note=""
        )

        # ✅ CREATE ITEM
        item = InvoiceItem.objects.create(
            Invoice=invoice,
            product=product,
            Qty=qty,
            Price=product.Price
        )

        # ✅ REDUCE STOCK
        product.stock -= qty
        product.save()

        # ✅ UPDATE TOTALS
        invoice.subtotal = item.Total
        invoice.final_total = item.Total
        invoice.save()

        return redirect('invoiceview')

    return render(request, 'invoice_form.html')


def edit_product(request, id):

    product = get_object_or_404(Product, id=id, companyName_id=request.session.get('org_id'))

    categories = Category.objects.all() 
    
    if request.method == "POST":

        product.Product_name = request.POST.get('Product_name') or product.Product_name
        product.Hsn_code = request.POST.get('Hsn_code') or product.Hsn_code
        product.Price = float(request.POST.get('Price') or product.Price)
        product.stock = int(request.POST.get('stock') or product.stock)
        product.Discount = int(request.POST.get('Discount') or product.Discount)
        product.Cgst = int(request.POST.get('Cgst') or product.Cgst)
        product.Sgst = int(request.POST.get('Sgst') or product.Sgst)
        product.Igst = int(request.POST.get('Igst') or product.Igst)
        product.Cess = int(request.POST.get('Cess') or product.Cess)

        product.save()
        messages.success(request, "Product updated successfully")
        return redirect('product_list')

    return render(request, 'productform.html', {
         'categories': categories,
        'product': product
    })
    
    
from django.shortcuts import get_object_or_404, redirect

def delete_product(request, id):

    if not request.session.get('org_id'):
        return redirect('login')

    product = get_object_or_404(
        Product,
        id=id,
        companyName_id=request.session.get('org_id')
    )

    product.delete()
    messages.success(request, "Product deleted successfully")

    return redirect('product_list')   # ✅ MUST MATCH urls.py


def customer_history(request, id):

    if not request.session.get('org_id'):
        return redirect('login')

    org_id = request.session.get('org_id')

    customer = CustomerDetails.objects.get(id=id)

    invoices = Invoice_Details.objects.filter(
        Cust_name=customer,
        companyName=org_id
    ).order_by('-Date')

    # attach products with each invoice
    invoice_data = []

    for inv in invoices:
        items = InvoiceItem.objects.filter(Invoice=inv)

        invoice_data.append({
            'invoice': inv,
            'items': items
        })

    total_spent = invoices.aggregate(total=Sum('final_total'))['total'] or 0

    return render(request, 'customer_history.html', {
        'customer': customer,
        'invoice_data': invoice_data,
        'total_spent': total_spent
    })

from .models import Category

from .models import Category, Product
from django.shortcuts import render, redirect, get_object_or_404

def category_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
        messages.success(request, "Category added successfully")
        return redirect('category_list')

    category = Category.objects.all()
    return render(request, 'category.html', {'category': category})


def delete_category(request, id):
    cat = get_object_or_404(Category, id=id)
    cat.delete()
    messages.success(request, "Category deleted successfully")
    return redirect('category_list')


from django.shortcuts import render
from .models import CustomerDetails, Invoice_Details, Product

from django.shortcuts import render
from .models import CustomerDetails, Invoice_Details, Product

from django.shortcuts import render
from .models import CustomerDetails, Invoice_Details, Product

def reports_view(request):
    # Fetch customers
    customers = CustomerDetails.objects.all()
    
    # Fetch invoices
    invoices = Invoice_Details.objects.all()
    
    # Products + sales
    products = Product.objects.all()
    product_sales = []
    for product in products:
        items = product.invoiceitem_set.all()  # related InvoiceItems
        total_sold = sum(item.Qty for item in items)
        total_amount = sum(item.Total for item in items)
        product_sales.append({
            'product': product,
            'total_sold': total_sold,
            'total_amount': total_amount
        })

    context = {
        'customers': customers,
        'invoices': invoices,
        'product_sales': product_sales
    }
    return render(request, 'reports.html', context)

from django.shortcuts import render, redirect
from .models import OrganisationDetails
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from django.shortcuts import render, redirect
from .models import OrganisationDetails
from django.contrib import messages

def settings_view(request):
    org = OrganisationDetails.objects.first()

    if request.method == "POST":
        # Organisation info
        org.company_name = request.POST.get("company_name")
        org.company_type = request.POST.get("company_type")
        org.pan_number = request.POST.get("pan_number")
        org.gstin_number = request.POST.get("gstin_number")
        org.address_1 = request.POST.get("address_1")
        org.address_2 = request.POST.get("address_2")
        org.state = request.POST.get("state")
        org.city = request.POST.get("city")
        org.pincode = request.POST.get("pincode")
        org.full_name = request.POST.get("full_name")
        org.phone = request.POST.get("phone")
        org.email = request.POST.get("email")

        # Logo upload
        if 'logo' in request.FILES:
            org.logo = request.FILES['logo']

        # Password change
        current = request.POST.get("current_password")
        new_pass = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")
        if current or new_pass or confirm:
            if current != org.password_1:
                messages.error(request, "Current password incorrect!")
            elif new_pass != confirm:
                messages.error(request, "New password and confirm do not match!")
            else:
                org.password_1 = new_pass
                org.password_2 = confirm
                messages.success(request, "Password updated successfully!")

        org.save()
        messages.success(request, "Settings updated successfully!")
        return redirect('settings')

    return render(request, 'settings.html', {'org': org})