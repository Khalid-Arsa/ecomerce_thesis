from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views


app_name = "ecomapp"
urlpatterns = [
    # Client side pages
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact-us/", ContactView.as_view(), name="contact"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="productdetail"),

    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),

    path("checkout/", CheckoutView.as_view(), name="checkout"),

    path("register/", CustomerRegistrationView.as_view(), name="customerregistration"),
    path('login/', CustomerLoginView.as_view(), name='customerlogin'),

    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),

    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path("order/", MyOrderView.as_view(), name="orderprofile"),
    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),

    path("search/", SearchView.as_view(), name="search"),

    path("forgot-password/", PasswordForgotView.as_view(), name="passworforgot"),
    path("password-reset/<email>/<token>/",
         PasswordResetView.as_view(), name="passwordreset"),

    path('mobile/', mobile, name='mobile'),
    path('mobile/<slug:data>', mobile, name='mobiledata'),



    # Admin Side pages
    path("admin-login", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    path("admin-order/<int:pk>/", AdminOrderDetailView.as_view(), name="adminorderdetail"),
    path("admin-all-orders/", AdminOrderListView.as_view(), name="adminorderlist"),

    path("admin-order-<int:pk>-change/", AdminOrderStatuChangeView.as_view(), name="adminorderstatuschange"),
    path("admin-track-number/<int:pk>/", tracking, name="admintracking"),

    path("admin-product/list/", AdminProductListView.as_view(), name="adminproductlist"),
    path("admin-product/add/", AdminProductCreateView.as_view(), name="adminproductcreate"),

    path("admin-received/", AdminReceivedView.as_view(), name="receivedorder"),
    path("admin-pending/", AdminPendingView.as_view(), name="pendingorder"),
    path("admin-processing/", AdminProcessingView.as_view(), name="processingorder"),
    path("admin-completed/", AdminCompletedView.as_view(), name="completedorder"),

    path("admin-manageuser/", AdminManageUserView.as_view(), name="manageuser"),
    path("admin-manageproduct/", AdminManageProductView.as_view(), name="manageproduct"),

    path("admin-manageuser-search/", AdminManageUserSearchView.as_view(), name="manageusersearch"),
    path("admin-manageproduct-search/", AdminManageProductSearchView.as_view(), name="manageproductsearch"),

    path("admin-product-update/<int:pk>", views.AdminProductAdmin, name="productupdate"),
    path("admin-product-delete/<int:pk>", views.AdminProductDelete, name="productdelete"),

    path("customer-profile-update/", views.CustomerUpdateProfile, name="profileupdate"),
    path('tracking-number/', tracking, name='tracking'),

    path('make_payment', make_payment, name='make_payment'),
    path('process_payment', process_payment, name='process_payment'),
    path('payment_failed', payment_failed, name='payment_failed'),
    path('payment_successful', payment_successful, name='payment_successful'),
    path('finalize_payment', finalize_payment, name='finalize_payment'),
]
