from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_cliente(request):

    if request.user.is_authenticated:
        return redirect('catalogo')

    if request.method == 'POST':

        usuario = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=usuario,
            password=password
        )

        if user:

            if user.is_staff:
                messages.error(
                    request,
                    'Este acceso es solo para clientes.'
                )
                return redirect('login')

            login(request, user)

            return redirect('catalogo')

        messages.error(
            request,
            'Usuario o contraseña incorrectos'
        )

    return render(
        request,
        'login.html'
    )


def logout_cliente(request):

    logout(request)

    return redirect('login')
