import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, ComprobanteForm  # Actualiza el import
from .models import Apartamento, PropietarioApartamento, Comprobante

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

# Modifica la vista dashboard_view

@login_required(login_url='login')
def dashboard_view(request):
    # Contar apartamentos del usuario
    total_apartamentos = request.user.apartamentos.count()
    # Contar comprobantes del usuario
    total_comprobantes = Comprobante.objects.filter(copropietario=request.user).count()
    
    return render(request, 'pagoprop/dashboard.html', {
        'user': request.user,
        'total_apartamentos': total_apartamentos,
        'total_comprobantes': total_comprobantes,
    })



# Nueva vista para mostrar apartamentos
@login_required(login_url='login')
def mis_apartamentos_view(request):
    # Buscar apartamentos del usuario logueado
    # through='PropietarioApartamento' nos permite hacer esta consulta
    apartamentos = request.user.apartamentos.all()
    
    # Enviar los apartamentos al template
    return render(request, 'pagoprop/mis_apartamentos.html', {
        'apartamentos': apartamentos
    })


# Vista para subir comprobantes
@login_required(login_url='login')
def subir_comprobante_view(request):
    if request.method == 'POST':
        # Crear formulario con los datos enviados
        form = ComprobanteForm(request.user, request.POST, request.FILES)
        
        if form.is_valid():
            # Guardar pero NO enviar a BD aún (commit=False)
            comprobante = form.save(commit=False)
            
            # Asignar el usuario logueado como copropietario
            comprobante.copropietario = request.user
            
            # AHORA SÍ guardar en la BD
            comprobante.save()
            
            messages.success(request, '¡Comprobante subido exitosamente!')
            return redirect('mis_comprobantes')
        else:
            messages.error(request, 'Error al subir el comprobante. Verifica los datos.')
    else:
        # GET: Mostrar formulario vacío
        form = ComprobanteForm(request.user)
    
    return render(request, 'pagoprop/subir_comprobante.html', {
        'form': form
    })


# Vista para ver mis comprobantes
@login_required(login_url='login')
def mis_comprobantes_view(request):
    # Traer TODOS los comprobantes del usuario logueado
    comprobantes = Comprobante.objects.filter(copropietario=request.user).order_by('-fecha_creacion')
    # ↑ .filter(): Solo los del usuario
    # ↑ .order_by('-fecha_creacion'): Más recientes primero (el - significa descendente)
    
    return render(request, 'pagoprop/mis_comprobantes.html', {
        'comprobantes': comprobantes
    })

# Vista para eliminar comprobante
@login_required(login_url='login')
def eliminar_comprobante_view(request, comprobante_id):
    try:
        comprobante = Comprobante.objects.get(comprobanteID=comprobante_id, copropietario = request.user)
    except Comprobante.DoesNotExist:
        messages.error(request, 'Comprobante no encontrado o no tienes permiso para eliminarlo.')
        return redirect('mis_comprobantes')
    
    #eliminar el archivo fisico del servidor
    if comprobante.archivo:
        if os.path.isfile(comprobante.archivo.path):
            os.remove(comprobante.archivo.path)

    #eliminar el registro de la base de datos
    comprobante.delete()
    
    messages.success(request, '¡Comprobante eliminado exitosamente!')
    return redirect('mis_comprobantes')