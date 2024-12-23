from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.MyView.as_view(), name='index'),
    path('order/', views.OrderView.as_view(), name='order'),
    # path('order/create/', views.OrderView.as_view(), name='createorder'),
    # path('order/update/<int:order_id>', views.OrderView.as_view(), name='createorder'),
    

    # add 'add to order button  on store detail'
    # add 'add to order button on product detail'

    path('order/add/<int:product_id>/', views.OrderView.as_view(), name='addorder'),
    path('order/clear/', views.ClearOrderView.as_view(), name='clearorder'),
    path('order/product/delete/<int:product_id>/', views.DeleteProductFromOrderView.as_view(), name='orderdeleteproduct'),
    

    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('stores/', views.StoresView.as_view(), name='stores'),
    path('stores/create/', views.CreateStoreView.as_view(), name='createstore'),
    path('stores/<int:store_id>/', views.StoreDetailView.as_view(), name='storedetail'),
    path('stores/update/<int:store_id>/', views.UpdateStoreView.as_view(), name='updatestore'),
    path('stores/update/<int:store_id>/address/', views.UpdateStoreAddressView.as_view(), name='storeupdateaddress'),
    path('stores/delete/<int:pk>/', views.DeleteStoreView.as_view(), name='deletestore'),

    path('stores/product/add/', views.AddProductView.as_view(), name='addstoreproduct'),
    path('stores/product/update/<int:product_id>/', views.UpdateProductView.as_view(), name='updatestoreproduct'),
    path('stores/product/image/update/<int:product_id>/', views.UpdateProductImageView.as_view(), name='updatestoreproductimage'),

    path('stores/product/delete/<int:product_id>/', views.DeleteProductView.as_view(), name='deletestoreproduct'),

    path('order/<int:order_id>/buy/', views.BuyView.as_view(), name='buy'),
    path('order/<int:order_id>/checkout/', views.CheckoutView.as_view(), name='checkout'),

    path('address/', views.ChangeAddressModalView.as_view(), name='address'),
    path('order/address/', views.OrderChangeAddressModalView.as_view(), name='orderaddress'),
    path('settings/address/', views.SettingsChangeAddressModalView.as_view(), name='settingsaddress'),

    path('address/create/', views.CreateAddressModalView.as_view(), name='createaddress'),
    path('order/address/create/', views.OrderCreateAddressModalView.as_view(), name='ordercreateaddress'),
    path('settings/address/create/', views.SettingsCreateAddressModalView.as_view(), name='settingscreateaddress'),

    path('order/address/update/<int:address_id>/', views.OrderUpdateAddressView.as_view(), name='orderupdateaddress'),
    path('settings/address/update/<int:address_id>/', views.SettingsUpdateAddressView.as_view(), name='settingsupdateaddress'),
    path('order/address/delete/<int:address_id>/', views.OrderDeleteAddressView.as_view(), name='orderdeleteaddress'),
    path('settings/address/delete/<int:address_id>/', views.SettingsDeleteAddressView.as_view(), name='settingsdeleteaddress'),

    path('latest-address/update/<int:address_id>/', views.LatestAddressView.as_view(), name='chooselatestaddress'),
    
    path('payment/success/', views.SuccessPaymentView.as_view(), name='paymentsuccess'),
    path('payment/error/', views.ErrorPaymentView.as_view(), name='paymenterror'),
    path('payment/unfinished/', views.UnfinishedPaymentView.as_view(), name='paymentunfinished'),

    path('api-test/', views.api_test, name='apitest'),
    path('uploadpreview/', views.upload_preview_image),
]