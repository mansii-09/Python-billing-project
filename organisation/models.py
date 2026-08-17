from django.db import models
# from django.contrib.auth.models import AbstractUser

# from django.contrib.auth.models import User

class OrganisationDetails(models.Model):
    company_name = models.CharField(max_length=50)
    company_type = models.CharField(max_length=50)
    pan_number = models.CharField(max_length=10)
    gstin_number = models.CharField(max_length=15)
    address_1 = models.CharField(max_length=90)
    address_2 = models.CharField(max_length=90)
    state = models.CharField(max_length=60)
    city = models.CharField(max_length=60)
    pincode = models.CharField(max_length=6)
    full_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email  = models.EmailField()
    user_id = models.CharField(max_length=40)
    password_1 = models.CharField(max_length=225)
    password_2 = models.CharField(max_length=225)
    logo = models.ImageField(upload_to='company_logo/', blank=True, null=True)


    def __str__(self):
        
        return self.company_name    

class CustomerDetails(models.Model):
    companyName = models.ForeignKey(OrganisationDetails, on_delete=models.CASCADE,default="")
    cust_name = models.CharField(max_length=50,verbose_name='Customer Name')
    cont_person = models.CharField(max_length=50,verbose_name='Contact Person')
    contact_num = models.IntegerField(verbose_name='Contact Number')
    email = models.CharField(max_length=50,default="")
    company_type = models.CharField(verbose_name='Company Type',max_length = 50)
    address = models.CharField(max_length=90,verbose_name='Address Line 1')
    address_2 = models.CharField(max_length=90,verbose_name='Address Line 2')
    landmark = models.CharField(max_length=50,verbose_name='Landmark')
    country = models.CharField(max_length=50,verbose_name='Country')
    state = models.CharField(max_length=50,verbose_name='State')
    city = models.CharField(max_length=50,verbose_name='City')
    pincode = models.IntegerField(verbose_name='Pincode')

    def __str__(self):
        return self.cust_name  


class PaymentQR(models.Model):

    companyName = models.ForeignKey(OrganisationDetails,on_delete=models.CASCADE)

    qr_image = models.ImageField(upload_to="payment_qr/")

    payment_link = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)


#--------------------------Invoice Page------------------->

#--------------------------Invoice Page------------------->

class Invoice_Details(models.Model):
    companyName = models.ForeignKey(OrganisationDetails, on_delete=models.CASCADE, default="")
    Cust_name = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE, default="")

    Invoice_type = models.CharField(max_length=50)

    # ⚠️ TEMP: NO UNIQUE (important for migration)
    Invoice_num = models.CharField(max_length=20, blank=True)

    Date = models.DateField(auto_now_add=True)

    Dispatch_through = models.CharField(max_length=50)
    Due_date = models.DateField(auto_now=False, blank=True)

    Bank = models.CharField(max_length=20)
    Payment_type = models.CharField(max_length=20)

    Payment_note = models.TextField(max_length=50)
    T_c = models.TextField(max_length=100)
    Document_note = models.TextField(max_length=100)

    qrcode = models.ImageField(upload_to="", default="", blank=True)

    # totals
    subtotal = models.FloatField(default=0)
    gst_total = models.FloatField(default=0)
    discount_total = models.FloatField(default=0)
    final_total = models.FloatField(default=0)

    def save(self, *args, **kwargs):

        if not self.Invoice_num:
            last = Invoice_Details.objects.order_by('-id').first()

            if last and last.Invoice_num:
                try:
                    num = int(last.Invoice_num.split('-')[-1]) + 1
                except:
                    num = 1
            else:
                num = 1

            self.Invoice_num = f"INV-{num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.Invoice_num


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#============== Product Details ==================>

class Product(models.Model):

    companyName = models.ForeignKey(OrganisationDetails, on_delete=models.CASCADE)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    Product_name = models.CharField(max_length=50)
    Hsn_code = models.CharField(max_length=20)

    Price = models.FloatField()

    Discount = models.IntegerField(default=0)
    Cgst = models.IntegerField(default=0)
    Sgst = models.IntegerField(default=0)
    Igst = models.IntegerField(default=0)
    Cess = models.IntegerField(default=0)

    stock = models.IntegerField(default=0)
  
    
    def __str__(self):
        return self.Product_name



class InvoiceItem(models.Model):

    Invoice = models.ForeignKey(Invoice_Details, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    Qty = models.IntegerField()
    Price = models.FloatField()

    Total = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):

        base = self.Qty * self.Price

        discount_amount = (base * self.product.Discount) / 100
        gst = ((self.product.Cgst + self.product.Sgst + self.product.Igst) * base) / 100

        self.Total = base + gst - discount_amount

        super().save(*args, **kwargs)
   
    
class Employee(models.Model):

    companyName = models.ForeignKey(OrganisationDetails, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    role = models.CharField(max_length=100)

    salary = models.IntegerField()

    joining_date = models.DateField()

    def __str__(self):
        return self.name
    
