from django.urls import path
from . import views

urlpatterns = [

    path(
        'reportes/',
        views.reportes_admin,
        name='reportes_admin'
    ),

]