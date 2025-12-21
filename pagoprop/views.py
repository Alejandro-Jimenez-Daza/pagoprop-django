import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, ComprobanteForm, FiltroComprobantesForm, EditarPerfilForm
from .models import Apartamento, PropietarioApartamento, Comprobante, User
# importo el paginador
from django.core.paginator import Paginator
#importo formulario de filtros
#staff
from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.models import User  # 👈 AGREGAR
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



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
    comprobantes_list = Comprobante.objects.filter(copropietario=request.user).order_by('-fecha_creacion')
    # ↑ .filter(): Solo los del usuario
    # ↑ .order_by('-fecha_creacion'): Más recientes primero (el - significa descendente)

    # CREAR FORMULARIO DE FILTROS
    filtro_form = FiltroComprobantesForm(request.user, request.GET)

    if filtro_form.is_valid():

        #filtrar por apartamento
        apartamento = filtro_form.cleaned_data.get('apartamento')
        if apartamento:
            comprobantes_list = comprobantes_list.filter(apartamento=apartamento)

        #filtrar por fecha desde
        fecha_desde = filtro_form.cleaned_data.get('fecha_desde')
        if fecha_desde:
            comprobantes_list = comprobantes_list.filter(fecha_creacion__date__gte=fecha_desde)
        
        #filtrar por fecha hasta
        fecha_hasta = filtro_form.cleaned_data.get('fecha_hasta')
        if fecha_hasta:
            comprobantes_list = comprobantes_list.filter(fecha_creacion__date__lte=fecha_hasta)

        #filtrar por monto minimo
        monto_minimo = filtro_form.cleaned_data.get('monto_minimo')
        if monto_minimo:
            comprobantes_list = comprobantes_list.filter(monto__gte=monto_minimo)

        #filtrar por monto maximo
        monto_maximo = filtro_form.cleaned_data.get('monto_maximo')
        if monto_maximo:
            comprobantes_list = comprobantes_list.filter(monto__lte=monto_maximo)


    # CREAR PAGINADOR {10 POR PAGINA}
    paginator = Paginator(comprobantes_list, 10)

    #obtener el numero de pagina actual desde la URL (?page = 2)
    page_number = request.GET.get('page')
    # ↑ Lee el parámetro ?page=2 de la URL
    # Si no existe, devuelve None

    #obtener los comprobantes de la pagina
    comprobantes= paginator.get_page(page_number)
    
    # ↑ Obtiene los comprobantes de esa página específica
    # Si page_number es None, devuelve la página 1
    # Si page_number es 999 (no existe), devuelve la última página

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


@login_required(login_url='login')
def editar_comprobante_view(request, comprobante_id):
    #buscar el comprobante
    try:
        comprobante = Comprobante.objects.get(comprobanteID=comprobante_id, copropietario= request.user)
    except Comprobante.DoesNotExist:
        messages.error(request, 'Comprobante no encontrado o no tienes permisos para editarlo.')
        return redirect('mis_comprobantes')
    
    if request.method == 'POST':
        form = ComprobanteForm(request.user, request.POST, request.FILES, instance=comprobante)

        if form.is_valid():
            form.save()
            messages.success(request, '¡Comprobante actualizado exitosamente!')
            return redirect('mis_comprobantes')
        else:
            messages.error(request,'Error al actualizar el comprobante.')

    else:
        #mostrar formulario pre-llenado
        form = ComprobanteForm(request.user, instance= comprobante)
    
    return render(request, 'pagoprop/editar_comprobante.html',{
        'form':form,
        'comprobante': comprobante
    })

#funcion de ver detalles del apartamento
@login_required(login_url='login')
def detalle_apartamento_view(request, apartamento_id):
    #buscar el apartamento
    try:
        apartamento = Apartamento.objects.get(apartamentoID=apartamento_id)
    except Apartamento.DoesNotExist:
        messages.error(request, 'Apartamento no encontrado.')
        return redirect('mis_apartamentos')
    
    #verficar que el usuario es propietario de ese apartamento
    if not PropietarioApartamento.objects.filter(copropietario = request.user, apartamento = apartamento).exists():
        messages.error(request, 'No tienes acceso a este apartamento.')
        return redirect('mis_apartamentos')
    
    #obtener comprobantes de este apartamento
    comprobantes = Comprobante.objects.filter(
        apartamento = apartamento,
        copropietario = request.user
    ).order_by('-fecha_creacion')


    #calcular estadisticas
    from django.db.models import Sum, Count, Avg
    stats = comprobantes.aggregate(
        total_pagado = Sum('monto'),
        cantidad_pagos = Count('comprobanteID'),
        promedio_pago = Avg('monto')
    )

    #obtener todos los propietarios del apartamento
    propietarios = PropietarioApartamento.objects.filter(apartamento=apartamento).select_related('copropietario')

    return render(request, 'pagoprop/detalle_apartamento.html', {
        'apartamento': apartamento,
        'comprobantes': comprobantes,
        'stats': stats,
        'propietarios':propietarios
    })


from django.contrib.admin.views.decorators import staff_member_required


# Dashboard del administrador
@staff_member_required(login_url='login')
def admin_dashboard_view(request):
    # Estadísticas generales del edificio
    from django.db.models import Sum, Count, Avg
    
    # Total de usuarios
    total_usuarios = User.objects.filter(is_superuser=False).count()
    
    # Total de apartamentos
    total_apartamentos = Apartamento.objects.count()
    
    # Total de comprobantes
    total_comprobantes = Comprobante.objects.count()
    
    # Total recaudado
    total_recaudado = Comprobante.objects.aggregate(total=Sum('monto'))['total'] or 0
    
    # Comprobantes recientes (últimos 10)
    comprobantes_recientes = Comprobante.objects.select_related(
        'copropietario', 'apartamento'
    ).order_by('-fecha_creacion')[:10]
    
    # Apartamentos sin propietarios
    apartamentos_sin_propietario = Apartamento.objects.annotate(
        num_propietarios=Count('propietario_apartamentos')
    ).filter(num_propietarios=0)
    
    return render(request, 'pagoprop/admin_dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_apartamentos': total_apartamentos,
        'total_comprobantes': total_comprobantes,
        'total_recaudado': total_recaudado,
        'comprobantes_recientes': comprobantes_recientes,
        'apartamentos_sin_propietario': apartamentos_sin_propietario,

    })

# ver todos los comprobantes
@staff_member_required(login_url='login')
def admin_todos_comprobantes_view(request):
    # obtener todos los comprobantes de todos los usuarios
    comprobantes_list = Comprobante.objects.select_related(
        'copropietario','apartamento'
    ).order_by('-fecha_creacion')

    #paginador
    paginator = Paginator(comprobantes_list,20)#20 registros por pagina
    page_number= request.GET.get('page')
    comprobantes = paginator.get_page(page_number)

    # estadisticas
    from django.db.models import Sum, Count
    stats= Comprobante.objects.aggregate(
        total=Sum('monto'),
        cantidad=Count('comprobanteID')
    )


    return render(request, 'pagoprop/admin_todos_comprobantes.html', {
        'comprobantes': comprobantes,
        'stats':stats
    })


# asignar apartamento a usuario (admin)
@staff_member_required(login_url='login')
def admin_asignar_apartamento_view(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        apartamento_id= request.POST.get('apartamento')

        try:
            usuario = User.objects.get(id=usuario_id)
            apartamento = Apartamento.objects.get(apartamentoID=apartamento_id)

            #verificar si ya existe la relacion
            if PropietarioApartamento.objects.filter(
                copropietario = usuario,
                apartamento = apartamento
            ).exists():
                messages.warning(request, 'Este usuario ya tiene asignado este apartamento.')
            else:
                PropietarioApartamento.objects.create(
                    copropietario = usuario,
                    apartamento = apartamento
                )
                messages.success(request, f'✅ Apartamento {apartamento.numeroApartamento} asignado a {usuario.get_full_name()}')
                return redirect('admin_asignar_apartamento')
        
        except (User.DoesNotExist, Apartamento.DoesNotExist):
            messages.error(request, 'Usuario o apartamento no encontrado.')

    # GET motrar formulario
    usuarios= User.objects.filter(is_superuser=False).order_by('first_name', 'last_name')
    apartamentos = Apartamento.objects.all().order_by('numeroApartamento')

    # asignaciones actuales
    asignaciones = PropietarioApartamento.objects.select_related(
        'copropietario', 'apartamento'
    ).order_by('apartamento__numeroApartamento')

    return render(request, 'pagoprop/admin_asignar_apartamento.html',{
        'usuarios': usuarios,
        'apartamentos': apartamentos,
        'asignaciones':asignaciones
    })

# Eliminar asignación de apartamento (Admin)
@staff_member_required(login_url='login')
def admin_eliminar_asignacion_view(request, asignacion_id):
    try:
        asignacion = PropietarioApartamento.objects.get(propietarioAptoID=asignacion_id)
        copropietario = asignacion.copropietario.get_full_name()
        apartamento = asignacion.apartamento.numeroApartamento
        
        asignacion.delete()
        
        messages.success(request, f'✅ Asignación eliminada: {copropietario} ya no tiene acceso al Apartamento {apartamento}')
    except PropietarioApartamento.DoesNotExist:
        messages.error(request, 'Asignación no encontrada.')
    
    return redirect('admin_asignar_apartamento')


# Vista de perfil
@login_required(login_url='login')
def perfil_view(request):
    return render(request, 'pagoprop/perfil.html', {
        'user': request.user
    })


# Editar perfil
@login_required(login_url='login')
def editar_perfil_view(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Perfil actualizado exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Error al actualizar el perfil. Verifica los datos.')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'pagoprop/editar_perfil.html', {
        'form': form
    })


# Cambiar contraseña
@login_required(login_url='login')
def cambiar_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            # Importante: Actualizar la sesión para que no cierre sesión
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Contraseña cambiada exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Error al cambiar la contraseña. Verifica los datos.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'pagoprop/cambiar_password.html', {
        'form': form
    })


