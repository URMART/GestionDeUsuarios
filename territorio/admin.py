from django.contrib import admin
from .models import Aprendiz, Actividades, Monitoria, Usuario

# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'correo', 'usuario', 'rol', 'foto', 'verFoto' )
    
    def verFoto(self, obj):
        #generar código html en el admin
        from django.utils.html import format_html
        foto = obj.foto.url
        return format_html(f"<a href='{foto}' target='_blank'><img src='{foto}' width='20%' /></a>")

@admin.register(Aprendiz)
class AprendizAdmin(admin.ModelAdmin):
    list_display = ('id','cedula', 'nombre', 'apellido','edad')
    search_fields = ['cedula', 'nombre', 'apellido']
    list_filter = ['cedula']
    list_editable = ['cedula','nombre'] 

    def edad(self, obj):
        from datetime import date
        #obtenemos la fecha del sistema
        hoy = date.today()

        edad = hoy.year - obj.fecha_nacimiento.year - ((hoy.month, hoy.day)<(obj.fecha_nacimiento.month, obj.fecha_nacimiento.day))

        return edad



@admin.register(Monitoria)
class MonitoriaAdmin(admin.ModelAdmin):
    list_display = ('cat', 'cedula','nombre','apellido', 'fecha_inicio', 'fecha_final' )
    search_fields = ['cat', 'fecha_inicio','aprendiz__cedula','aprendiz__nombre','aprendiz__apellido']
    

    def nombre(self, obj):
        return obj.aprendiz.nombre

    def apellido(self, obj):
        return obj.aprendiz.apellido

    def cedula(self, obj):
        return obj.aprendiz.cedula
    


@admin.register(Actividades)
class ActividadesAdmin(admin.ModelAdmin):
    list_display = ('monitoria', 'actividad', 'observaciones', 'fecha')
    search_fields = ['monitoria', 'actividad', 'observaciones', 'fecha']

