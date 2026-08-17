from django.shortcuts import render, get_object_or_404, redirect
from organisation.models import OrganisationDetails, CustomerDetails, Invoice_Details, Product, Employee


def admin_dashboard(request):

    total_org = OrganisationDetails.objects.count()
    total_customers = CustomerDetails.objects.count()
    total_invoices = Invoice_Details.objects.count()
    total_employees = Employee.objects.count()

    invoices = Invoice_Details.objects.select_related('Cust_name').order_by('-id')[:3]

    organisations = OrganisationDetails.objects.order_by('-id')[:3]


    context = {

        "total_org": total_org,
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "total_employees": total_employees,
        "invoices": invoices,
        "organisations": organisations,

    }

    return render(request, "adminpanel/dashboard.html", context)



from django.shortcuts import render, redirect, get_object_or_404
from organisation.models import OrganisationDetails


# =========================
# Organisation List
# =========================

def organisations_page(request):

    organisations = OrganisationDetails.objects.all().order_by("-id")

    context = {
        "organisations": organisations
    }

    return render(request,"adminpanel/organisations.html",context)



# =========================
# Add Organisation
# =========================

def add_organisation(request):

    if request.method == "POST":

        OrganisationDetails.objects.create(

            company_name = request.POST.get("company_name"),
            company_type = request.POST.get("company_type"),
            pan_number = request.POST.get("pan_number"),
            gstin_number = request.POST.get("gstin_number"),
            address_1 = request.POST.get("address_1"),
            address_2 = request.POST.get("address_2"),
            state = request.POST.get("state"),
            city = request.POST.get("city"),
            pincode = request.POST.get("pincode"),
            full_name = request.POST.get("full_name"),
            phone = request.POST.get("phone"),
            email = request.POST.get("email"),

        )

        return redirect("organisations")

    return render(request,"adminpanel/add_organisation.html")



# =========================
# Update Organisation
# =========================

def update_organisation(request,id):

    org = get_object_or_404(OrganisationDetails,id=id)

    if request.method == "POST":

        org.company_name = request.POST.get("company_name")
        org.company_type = request.POST.get("company_type")
        org.phone = request.POST.get("phone")
        org.city = request.POST.get("city")

        org.save()

        return redirect("organisations")

    context = {"org":org}

    return render(request,"adminpanel/update_organisation.html",context)



# =========================
# Delete Organisation
# =========================

def delete_organisation(request,id):

    org = get_object_or_404(OrganisationDetails,id=id)
    org.delete()

    return redirect("organisations")


# =========================
# Customers Page + Search
# =========================

def customers_page(request):

    search = request.GET.get("search")

    if search:
        customers = CustomerDetails.objects.filter(cust_name__icontains=search)
    else:
        customers = CustomerDetails.objects.all().order_by("-id")

    context = {
        "customers": customers,
        "search": search
    }

    return render(request, "adminpanel/customers.html", context)


# =========================
# Add Customer
# =========================

def add_customer(request):

    orgs = OrganisationDetails.objects.all()

    if request.method == "POST":

        CustomerDetails.objects.create(

            companyName_id=request.POST.get("company"),
            cust_name=request.POST.get("cust_name"),
            cont_person=request.POST.get("cont_person"),
            contact_num=request.POST.get("contact_num"),
            email=request.POST.get("email"),
            company_type=request.POST.get("company_type"),
            address=request.POST.get("address"),
            address_2=request.POST.get("address_2"),
            landmark=request.POST.get("landmark"),
            country=request.POST.get("country"),
            state=request.POST.get("state"),
            city=request.POST.get("city"),
            pincode=request.POST.get("pincode"),
        )

        return redirect("customers")

    return render(request, "adminpanel/add_customer.html", {"orgs": orgs})


# =========================
# Update Customer
# =========================

def update_customer(request, id):

    customer = get_object_or_404(CustomerDetails, id=id)
    orgs = OrganisationDetails.objects.all()

    if request.method == "POST":

        customer.companyName_id = request.POST.get("company")
        customer.cust_name = request.POST.get("cust_name")
        customer.cont_person = request.POST.get("cont_person")
        customer.contact_num = request.POST.get("contact_num")
        customer.email = request.POST.get("email")
        customer.city = request.POST.get("city")

        customer.save()

        return redirect("customers")

    context = {
        "customer": customer,
        "orgs": orgs
    }

    return render(request, "adminpanel/update_customer.html", context)

# =========================
# Delete Customer
# =========================

def delete_customer(request, id):

    customer = get_object_or_404(CustomerDetails, id=id)
    customer.delete()

    return redirect("customers")


# =========================
# Invoice List + Search
# =========================

def invoices_page(request):

    search = request.GET.get("search")

    if search:
        invoices = Invoice_Details.objects.filter(Invoice_num__icontains=search)
    else:
        invoices = Invoice_Details.objects.all().order_by("-id")

    context = {
        "invoices": invoices,
        "search": search
    }

    return render(request,"adminpanel/invoices.html",context)



# =========================
# Add Invoice
# =========================

def add_invoice(request):

    orgs = OrganisationDetails.objects.all()
    customers = CustomerDetails.objects.all()

    if request.method == "POST":

        Invoice_Details.objects.create(

            companyName_id=request.POST.get("company"),
            Cust_name_id=request.POST.get("customer"),
            Invoice_type=request.POST.get("invoice_type"),
            Invoice_num=request.POST.get("invoice_num"),
            Date=request.POST.get("date"),
            Dispatch_through=request.POST.get("dispatch"),
            Due_date=request.POST.get("due_date"),
            Bank=request.POST.get("bank"),
            Payment_type=request.POST.get("payment_type"),
            Payment_note=request.POST.get("payment_note"),
            T_c=request.POST.get("terms"),
            Document_note=request.POST.get("doc_note"),
        )

        return redirect("invoices")

    context = {
        "orgs": orgs,
        "customers": customers
    }

    return render(request,"adminpanel/add_invoice.html",context)



# =========================
# Update Invoice
# =========================

def update_invoice(request, id):

    invoice = get_object_or_404(Invoice_Details, id=id)

    orgs = OrganisationDetails.objects.all()
    customers = CustomerDetails.objects.all()

    if request.method == "POST":

        invoice.companyName_id = request.POST.get("company")
        invoice.Cust_name_id = request.POST.get("customer")

        invoice.Invoice_type = request.POST.get("invoice_type")
        invoice.Invoice_num = request.POST.get("invoice_num")

        invoice.Date = request.POST.get("date")
        invoice.Due_date = request.POST.get("due_date")

        invoice.Dispatch_through = request.POST.get("dispatch")
        invoice.Bank = request.POST.get("bank")

        invoice.Payment_type = request.POST.get("payment_type")
        invoice.Payment_note = request.POST.get("payment_note")

        invoice.T_c = request.POST.get("terms")
        invoice.Document_note = request.POST.get("doc_note")

        invoice.save()

        return redirect("invoices")

    context = {
        "invoice": invoice,
        "orgs": orgs,
        "customers": customers
    }

    return render(request, "adminpanel/update_invoice.html", context)


# =========================
# Delete Invoice
# =========================

def delete_invoice(request,id):

    invoice = get_object_or_404(Invoice_Details,id=id)
    invoice.delete()

    return redirect("invoices")


# =========================
# Product List + Search
# =========================

def products_page(request):

    search = request.GET.get("search")

    if search:
        products = Product.objects.filter(Product_name__icontains=search)
    else:
        products = Product.objects.all().order_by("-id")

    context = {
        "products": products,
        "search": search
    }

    return render(request,"adminpanel/products.html",context)


# =========================
# Add Product
# =========================

def add_product(request):
    orgs = OrganisationDetails.objects.all()
    categories = Category.objects.all()  # Fetch categories to send to template

    if request.method == "POST":
        Product.objects.create(
            companyName_id=request.POST.get("company"),
            category_id=request.POST.get("category"),  # <-- Add this line
            Product_name=request.POST.get("product_name"),
            Hsn_code=request.POST.get("hsn") or '',
            Price=float(request.POST.get("price") or 0),
            Discount=int(request.POST.get("discount") or 0),
            Cgst=int(request.POST.get("cgst") or 0),
            Sgst=int(request.POST.get("sgst") or 0),
            Igst=int(request.POST.get("igst") or 0),
            Cess=int(request.POST.get("cess") or 0),
            stock=int(request.POST.get("stock") or 0),
        )
        return redirect("aproducts")

    context = {
        "orgs": orgs,
        "categories": categories,  # <-- Pass categories to template
    }

    return render(request, "adminpanel/add_product.html", context)


# =========================
# Update Product
# =========================

def update_product(request,id):

    product = get_object_or_404(Product,id=id)

    orgs = OrganisationDetails.objects.all()

    if request.method == "POST":

        product.companyName_id=request.POST.get("company")

        product.Product_name=request.POST.get("product_name")
        product.Hsn_code=request.POST.get("hsn") or ''

        product.Price=float(request.POST.get("price") or product.Price)
        product.Discount=int(request.POST.get("discount") or product.Discount)

        product.Cgst=int(request.POST.get("cgst") or product.Cgst)
        product.Sgst=int(request.POST.get("sgst") or product.Sgst)
        product.Igst=int(request.POST.get("igst") or product.Igst)
        product.Cess=int(request.POST.get("cess") or product.Cess)

        product.stock=int(request.POST.get("stock") or product.stock)

        product.save()

        return redirect("aproducts")

    context={
        "product":product,
        "orgs":orgs,
    }

    return render(request,"adminpanel/update_product.html",context)


# =========================
# Delete Product
# =========================

def delete_product(request,id):

    product = get_object_or_404(Product,id=id)
    product.delete()

    return redirect("aproducts")


# =========================
# Employee List + Search
# =========================

def employees_page(request):

    search = request.GET.get("search")

    if search:
        employees = Employee.objects.filter(name__icontains=search)
    else:
        employees = Employee.objects.all().order_by("-id")

    context = {
        "employees": employees,
        "search": search
    }

    return render(request, "adminpanel/employees.html", context)


# =========================
# Add Employee
# =========================

def add_employee(request):

    orgs = OrganisationDetails.objects.all()

    if request.method == "POST":

        Employee.objects.create(

            companyName_id=request.POST.get("company"),

            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),

            role=request.POST.get("role"),
            salary=request.POST.get("salary"),

            joining_date=request.POST.get("joining_date"),
        )

        return redirect("employees_page")

    context = {"orgs": orgs}

    return render(request, "adminpanel/add_employee.html", context)


# =========================
# Update Employee
# =========================

def update_employee(request, id):

    employee = get_object_or_404(Employee, id=id)
    orgs = OrganisationDetails.objects.all()

    if request.method == "POST":

        employee.companyName_id = request.POST.get("company")

        employee.name = request.POST.get("name"),
        employee.email = request.POST.get("email"),
        employee.phone = request.POST.get("phone"),

        employee.role = request.POST.get("role"),
        employee.salary = request.POST.get("salary"),

        employee.joining_date = request.POST.get("joining_date")

        employee.save()

        return redirect("employees_page")

    context = {
        "employee": employee,
        "orgs": orgs
    }

    return render(request, "adminpanel/update_employee.html", context)


# =========================
# Delete Employee
# =========================

def delete_employee(request, id):

    employee = get_object_or_404(Employee, id=id)
    employee.delete()

    return redirect("employees_page")
