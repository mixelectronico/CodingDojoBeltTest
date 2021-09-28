from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from time import gmtime, strftime
from django.db.models import Count

from .models import *

# Create your views here.
def login(request):
    if 'user_id' in request.session:
        user_tips_list = Trip.objects.filter(creador=request.session['user_id']) | Trip.objects.filter(usuario_unido=request.session['user_id'])
        other_trips_list = Trip.objects.exclude(creador=request.session['user_id']).exclude(usuario_unido=request.session['user_id'])
        context = {
        "trips": user_tips_list,
        "other_plans": other_trips_list,
        }
        return render(request, 'home.html', context)
    return render(request, 'registrame.html')


def registrar(request):
    return render(request, 'registrame.html')


def inicio_sesion(request):
    usuario = User.objects.filter(email=request.POST['email_login'].lower())
    errores = User.objects.validar_login(request.POST['pass_login'], usuario)

    if len(errores) > 0:
        for key, msg in errores.items():
            messages.error(request, msg)
        return redirect('/')
    else:
        request.session['user_id'] = usuario[0].id
        request.session['user_name'] = usuario[0].nombre
        return redirect('login')


def registro(request):
    #validacion de parametros
    errors = User.objects.basic_validator(request.POST)

    if len(errors) > 0:
        for key, msg in errors.items():
            messages.error(request, msg)
        return redirect('/registrar')

    else:
        #encriptar password
        password = User.objects.encriptar(request.POST['password'])
        
        rol = 2
        if User.objects.all().count() == 0:
            rol = 1

        #crear usuario
        user = User.objects.create(
            nombre=request.POST['nombre'],
            alias=request.POST['alias'],
            email=request.POST['email'],
            password=password,
            rol=rol,
        )
        #request.session['user_id'] = user.id
        #retornar mensaje de creacion correcta
        msg="Usuario creado exitosamente!"
        messages.success(request, msg)
    return redirect('/')


def logout(request):
    request.session.flush()
    return redirect('/')


def cambiar_pass(request):
    reg_user = User.objects.filter(id=request.session['user_id'])
    errores = User.objects.validar_login(request.POST['pass_actual'], reg_user)
    
    if len(errores) > 0:
        for key, msg in errores.items():
            messages.error(request, msg)
        return render(request, 'recuperar.html')
    else:
        pass_nueva = request.POST['pass_nueva']
        pass_confirm = request.POST['pass_confirmacion']
        if len(pass_nueva) < 6:
            messages.error(request, "nuevo password debe ser mayor o igual a 6 caracteres", extra_tags='pass_nueva')
            return render(request, 'recuperar.html')

        mensaje = User.objects.comparar_password(pass_nueva,pass_confirm)
        print(mensaje)
        if len(mensaje) > 0:
            messages.error(request, mensaje)
            return render(request, 'recuperar.html')
        
        password_encriptado = User.objects.encriptar(pass_nueva)

        reg_user[0].password = password_encriptado
        reg_user[0].save()
        request.session.flush()
        return redirect('/')

def recuperar(request):
    reg_user = User.objects.get(id=request.session['user_id'])

    context = {
        "active_user": reg_user,
    }
    return render(request, 'recuperar.html', context)

# --------------------------------
# Metodos relacionados a los viajes

def add_trip(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        destination = request.POST['destination']
        description = request.POST['description']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        errors = Trip.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for key, msg in errors.items():
                messages.error(request, msg)
            return redirect('add_trip')

        Trip.objects.create(destino=destination, descripcion=description, fecha_inicio=start_date, fecha_termino=end_date,
                            creador=user)
        return redirect('login')

    return render(request, 'formulario_viaje.html')


def join_plan(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        print(user)
        travel_plan = Trip.objects.get(id=request.POST['trip_id'])
        travel_plan.usuario_unido.add(user)
    return redirect('login')

def show_trip(request):
    if request.method == 'POST':
        context = {
            'viaje': Trip.objects.get(id=request.POST['trip_id'])
        }
        return render(request, 'viaje.html', context)
    return redirect('login')
    