import time
import threading
from django.views.generic import TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
import random
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.db.models import Q
from .forms import *
from django.views import View
from django.contrib import messages
import base64
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from django.http import JsonResponse
from paymongo import Paymongo

secret_key = "sk_test_aZneKHAGmDyZFXcanMoJ2haj"


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "Dipak Niroula"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
        print(page_number)
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                    subtotal=product_obj.selling_price
                )
                cart_obj.total += product_obj.selling_price

                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context


def crawl(tracking):
    content = list()
    if tracking is not None:
        b64 = base64.b64encode(tracking.encode('ascii')).decode('ascii')
        response = requests.get(f"https://www.lbcexpress.com/track/{b64}").content
        soup = BeautifulSoup(response, "html.parser")
        status = [x.get_text() for x in soup.find_all(class_='status-tracking')]
        time = [z.get_text() for z in soup.find_all(class_='date-track-a')]
        content.append({'status': status, 'time': time})
    else:
        content.append({'status': "", 'time': ""})
    return content


def tracking(request):
    data = list({'status': 'Null', 'time': 'Null'})
    if 'number' in request.GET:
        # Fetch weather data
        tracking = request.GET.get('number')
        data = crawl(tracking)
    return render(request, 'tracking.html', {'data': data[0]})


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("ecomapp:mycart")


def mobile(request, data=None):
    if data == None:
        mobile = Product.objects.filter(category='M')
    elif data == 'Samsung' or data == 'Apple':
        mobile = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'Huawei' or data == 'Nokia':
        mobile = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'LG' or data == 'Lenovo':
        mobile = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'Oppo' or data == 'Vivo':
        mobile = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'CherryMobile' or data == 'Xiaomi':
        mobile = Product.objects.filter(category='M').filter(brand=data)

    context = {'mobile': mobile}
    return render(request, 'mobile.html', context)


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("ecomapp:mycart")


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecomapp:mycart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("ecomapp:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None

        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            form.instance.transaction_id = generate_id(False)
            form.cleaned_data.get("fullname")
            form.cleaned_data.get("mobile")
            form.cleaned_data.get("email")
            form.cleaned_data.get("barangay")
            form.cleaned_data.get("street")
            form.cleaned_data.get("city")
            form.cleaned_data.get("province")
            form.cleaned_data.get("postal")

            del self.request.session['cart_id']
            order = form.save()

            return redirect(reverse("ecomapp:make_payment") + "?o_id=" + str(order.id))

        else:
            return redirect("ecomapp:make_payment")


def generate_id(is_num=False):
    saltable_string = "1234567890abcdefghijklmnopqrstuvwxyz"
    saltable_string_num = "1234567890"
    id = ""
    for x in range(10):
        id += (saltable_string[random.randint(0, 35)] if is_num else saltable_string_num[random.randint(0, 9)])
    return id


def make_payment(request):
    order_id = request.GET.get('o_id')
    order = Order.objects.get(id=order_id)
    order_all = Order.objects.filter(id=order_id)

    # create payload
    product_payload = {
        "total": int(str(format(order.total, '.2f')).replace('.', '')),
        "transact_id": order.transaction_id
    }
    if order_id is None:
        return redirect(reverse('ecomapp:home'))

    else:
        form = CreditCardForm()
    return render(request, 'process_payment.html', {'form': form, 'product_payload': product_payload})


# Data Entrypoint only
def process_payment(request):
    payment_payload = {}

    if request.method == 'POST':
        method = request.POST.get('method')
        payment_handler = {}
        product_payload = {
            'total': int(request.POST.get('total')),
            'transaction_id': str(f"{request.POST.get('transaction_id')}")
        }

        if method == "credit":
            payment_handler = credit_payment(request.POST.get('cc_number'),
                                             int(str(request.POST.get('cc_expiry')).split('/')[1]),
                                             int(str(request.POST.get('cc_expiry')).split('/')[0]),
                                             request.POST.get('cc_code'), product_payload)
        elif method == "gcash":
            payment_handler = ewallet_payment_intent(request, product_payload)

        return JsonResponse(payment_handler)


# Credit Card
def credit_payment(card_num, exp_year, exp_month, cvc, transaction_data):
    paymongo = Paymongo(secret_key)
    payment_method_payload = {
        "data": {
            "attributes": {"type": "card",
                           "details": {"card_number": card_num, "exp_month": exp_month, "exp_year": exp_year,
                                       "cvc": cvc}
                           }
        }
    }
    payment_intent_payload = {
        "data": {
            "attributes": {"amount": transaction_data['total'], "payment_method_allowed": ["card"],
                           "description": transaction_data['transaction_id'],
                           "statement_descriptor": "test2",
                           "payment_method_options": {"card": {"request_three_d_secure": "automatic"}},
                           "currency": "PHP"}
        }
    }
    intent_data = paymongo.payment_intents.create(payment_intent_payload)
    method_data = paymongo.payment_methods.create(payment_method_payload)
    intent_id = intent_data['id']
    method_id = method_data['id']

    payload = {
        "data": {
            "attributes": {
                "client_key": intent_id,
                "payment_method": method_id
            }

        }
    }

    return paymongo.payment_intents.attach(intent_id, payload)


# GCash
def ewallet_payment_intent(request, transaction_data):
    paymongo = Paymongo(secret_key)
    payment_source_payload = {
        "data": {
            "attributes": {"type": "gcash",
                           "amount": int(transaction_data['total']),
                           "currency": "PHP",
                           "redirect": {
                               "success": str(request.build_absolute_uri(f"{reverse('ecomapp:payment_successful')}?order_id={transaction_data['transaction_id']}")),
                               "failed": str(request.build_absolute_uri(reverse('ecomapp:payment_failed')))
                           }
                           }
        }
    }
    response_source = paymongo.sources.create(payment_source_payload)
    return response_source


def finalize_payment(request):
    paymongo = Paymongo(secret_key)
    time.sleep(15)
    payment_payload = {
        "data": {
            "attributes": {"description": str(request.GET['transaction_id']),
                           "statement_descriptor": "Mina Gadget Store",
                           "amount": int(request.GET['amount']),
                           "currency": "PHP",
                           "source": {
                               "id": request.GET['api_id'],
                               "type": "source"
                           }
                           }
        }
    }
    return JsonResponse(paymongo.payments.create(payment_payload))


def payment_successful(request):
    return render(request, "payment_done.html")


def payment_failed(request):
    return render(request, "payment_cancelled.html")


class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecomapp:home")


class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class MyOrderView(TemplateView):
    template_name = "order.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecomapp:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(Q(title__icontains=kw))
        context["results"] = results
        return context


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
                       "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("ecomapp:passworforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)


# admin pages
class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"


class AdminOrderStatuChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("ecomapp:adminorderdetail", kwargs={"pk": order_id}))


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"


class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("ecomapp:manageproduct")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)


class AdminReceivedView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminreceivedorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["receivedorders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context


class AdminPendingView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminpendingorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Pending").order_by("-id")
        return context


class AdminProcessingView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminprocessingorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["processingorders"] = Order.objects.filter(order_status="Order Processing").order_by("-id")
        return context


class AdminCompletedView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/admincompletedorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completedorders"] = Order.objects.filter(order_status="Order Completed").order_by("-id")
        return context


class AdminManageUserView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminmanageuser.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manageuser"] = Customer.objects.all().order_by("-id")
        return context


class AdminManageUserSearchView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminmanageusersearch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("search")
        results = Customer.objects.filter(Q(id__icontains=kw))
        context["results"] = results
        return context


class AdminManageProductView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminmanageproduct.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manageproduct"] = Product.objects.all().order_by("-id")
        return context


class AdminManageProductSearchView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminmanageproductsearch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("search")
        results = Product.objects.filter(Q(title__icontains=kw))
        print(results)
        context["results"] = results
        return context


def AdminProductAdmin(request, pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('ecomapp:manageproduct')

    context = {
        'form': form,
    }

    return render(request, 'adminpages/adminproductupdate.html', context)

def AdminTrackingView(request, pk):
    track = Order.objects.get(id=pk)
    form = TrackingForm(instance=track)
    if request.method == 'POST':
        form = TrackingForm(request.POST, instance=track)
        if form.is_valid():
            form.save()
            return redirect('ecomapp:receivedorder')

    context = {
        'form': form,
    }

    return render(request, 'adminpages/adminproductupdate.html', context)


def AdminProductDelete(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('ecomapp:manageproduct')

    context = {'product': product}

    return render(request, 'adminpages/adminproductdelete.html', context)



@login_required
def CustomerUpdateProfile(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Congratulations! Profile Updated Successfully')

    context = {'form': form}
    return render(request, 'customerupdateprofile.html', context)
