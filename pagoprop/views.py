from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm

# Vista de Registro
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error en el registro. Verifica los datos.')
    else:
        form = RegistroForm()
    
    return render(request, 'pagoprop/registro.html', {'form': form})

# Vista de Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'pagoprop/login.html', {'form': form})

# Vista de Logout
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# Vista de Dashboard (requiere login)
@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'pagoprop/dashboard.html', {
        'user': request.user
    })