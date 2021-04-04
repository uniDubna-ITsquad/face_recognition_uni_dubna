from django.urls import path

from . import views

urlpatterns = [
    path('media/', views.index, name='index'),
    path('media/<str:cam_ip>', views.cam, name='cam'),
    path(
        'media/<str:cam_ip>/<int:year>/<int:month>/<int:day>/preview',
        views.cam_preview, name='cam_preview'
    )

    # path('')
]