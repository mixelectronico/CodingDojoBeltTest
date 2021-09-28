from django.db import models
import re
import bcrypt
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime

# Create your models here.
class UserManager(models.Manager):
    def basic_validator(self, postData):
        errores = {}
        if len(User.objects.filter(email=postData['email'])) > 0:
            errores['existe'] = "Email ya registrado"
        else:
            if len(postData['nombre']) == 0:
                errores['nombre'] = "Nombre es obligatorio"
            if len(postData['alias']) == 0:
                errores['alias'] = "Alias es obligatorio"
            EMAIL = re.compile(
                r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
            if not EMAIL.match(postData['email']):
                errores['email'] = "email invalido"
            if len(postData['password']) < 6:
                errores['password'] = "Password debe ser mayor a 6 caracteres"

            val_pass = self.comparar_password(postData['password'],postData['password2'])
            if len(val_pass) > 0:
                errores['password'] = val_pass

        return errores

    def encriptar(self, password):
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return password.decode('utf-8')

    def validar_login(self, password, usuario ):
        errores = {}
        if len(usuario) > 0:
            pw_hash = usuario[0].password

            if bcrypt.checkpw(password.encode(), pw_hash.encode()) is False:
                errores['pass_incorrecto'] = "password es incorrecto"
        else:
            errores['usuario_invalido'] = "Usuario no existe"
        return errores
    
    def comparar_password(self,password, password2):
        if password != password2:
            return "Password no son iguales"
        else:
            return ""


class User(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    alias = models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    password = models.CharField(max_length=255)
    rol = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class TripManager(models.Manager):
    def basic_validator(self, postData):
        today = make_aware(timezone.now().today())

        errores = {}
        if len(postData['destination']) == 0:
            errores['destination'] = "Destination field cannot be empty"

        if len(postData['description']) == 0:
            errores['description'] = "Description field cannot be empty"

        if len(postData['start_date']) == 0:
            errores['start_date'] = "Starting travel date field cannot be empty"
            if len(postData['end_date']) == 0:
                errores['end_date'] = "Ending travel date field cannot be empty"
        else:
            start_date = make_aware(datetime.strptime(postData['start_date'], '%Y-%m-%d'))
            if start_date <= today:
                errores['start_date'] = "The starting date must be in the future"

            if len(postData['end_date']) == 0:
                errores['end_date'] = "Ending travel date field cannot be empty"
            else:
                end_date = make_aware(datetime.strptime(postData['end_date'], '%Y-%m-%d'))
                if end_date <= start_date:
                    errores['end_date'] = "Ending travel date field cannot be before the starting date"

        return errores


class Trip(models.Model):
    creador = models.ForeignKey(User, related_name="sus_viajes", on_delete=models.CASCADE)
    destino = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=200, default="")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    usuario_unido = models.ManyToManyField(User, related_name="sus_viajes_unidos", blank=True, null=True)
    objects = TripManager()
    