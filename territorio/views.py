from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Mensajes tipo cookie temporales
from django.contrib import messages

#Gestión de Errores de base de datos
from django.db import IntegrityError

#Para paginado
from django.core.paginator import Paginator

#Almacenamiento y gestión de archivos o fotos
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from os import remove, path 
BASE_DIR = Path(__file__).resolve().parent.parent

from .models import Aprendiz, Actividades, Monitoria, Usuario

#Cifrado de claves
from .crypt import claveEncriptada

# Create your views here.

def loginFormulario(request):
    return render(request,'territorio/login/login.html')

def login(request):
    if request.method == "POST":
        try:
            #capturar datos del formulario
            user = request.POST["usuario"]
            pasw = claveEncriptada(request.POST["clave"])
            print(pasw)
            #verificar si existe en base de datos
            q = Usuario.objects.get(usuario = user, password = pasw)
            
            #crear la variable de sesion
            #Transformar valores de sesion a dict *********************
            request.session["logueo"] = [q.id, q.nombre, q.apellido, q.rol, q.get_rol_display()]
            return redirect('territorio:index')
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos...")
            return redirect('territorio:loginFormulario')
    else:
        messages.warning(request, "Usted no envió datos...")
        return redirect('territorio:loginFormulario')

def logout(request):
    try:
        del request.session["logueo"]
        messages.success(request, "Sesión cerrada correctamente!")
    except Exception as e:
        messages.error(request, "Ocurrió un error, intente de nuevo...")
    
    return redirect('territorio:index')

def perfil(request):
    login = request.session.get('logueo', False)
    q = Usuario.objects.get(pk = login[0])
    contexto = { "perfil": q }
    return render(request, 'territorio/usuarios/perfil.html', contexto)

def actualizarPerfil(request):
    if request.method == "POST":
        try:
            login = request.session.get('logueo', False)
            q = Usuario.objects.get(pk = login[0])
            q.nombre = request.POST["nombre"]
            q.apellido = request.POST["apellido"]
            q.correo = request.POST["correo"]
            #control de cambio de datos único en DB.............
            if q.usuario != request.POST["usuario"]:
                try:
                    consulta = Usuario.objects.get(usuario = request.POST["usuario"])
                    raise Exception("Usuario ya existe....")
                except Usuario.DoesNotExist:
                    messages.debug(request, "-- Resultado consulta usuario: OK")
                    q.usuario = request.POST["usuario"]
                    
            else:
                messages.debug(request, "-- No hay cambios en el usuario...... OK")
                q.usuario = request.POST["usuario"]
            
            if request.POST["password"] != "":
                q.password = claveEncriptada(request.POST["password"])
            
            q.save()
            
            #Enviar correo
            from django.core.mail import send_mail
            try:
                send_mail(
                    'Correo de prueba',
                    'Hola como estás te escribo desde Django Territorio para informar que tus datos fueron actualizados correctamente.',
                    'correosadso@gmail.com',
                    ['jor@misena.edu.co'],
                    fail_silently=False,
                )
                messages.info(request, "Correo enviado!")
            except Exception as e:
                messages.error(request, f"Error: {e}")
            #-------------
            
            #Cambiar algunos datos de la sesion
            login[1] = q.nombre
            login[2] = q.apellido
            request.session["logueo"] = login
            
            messages.success(request, "Perfil actualizado correctamente!")
        except Usuario.DoesNotExist:
            messages.error(request, "No existe el usuario...")    
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        messages.warning(request, "No envió datos...")
    
    return redirect('territorio:perfil')

def loginRequerido(funcionVerificada):
    def resultante(*args, **kwargs):
        print("Revisando autenticación....")
        resultado = funcionVerificada(*args, **kwargs)
        print("Listo...")
        return resultado
    
    return resultante

@loginRequerido
def inicio(request):
    #return HttpResponse(request, 'territorio/index.html')

    return render(request,'territorio/index.html')

#Reto, construir un decorador para control de autenticación... ****
def aprendices(request):
    login = request.session.get('logueo', False)
    if login and (login[3] == "R" or login[3] == "I"):
        q = Aprendiz.objects.all()
        
        pag = Paginator(q, 4)   #cinco registros por página
        page_number = request.GET.get('page')
        
        #sobreescribo el query
        q = pag.get_page(page_number)
        
        contexto = {'page_obj': q}

        return render(request,'territorio/aprendices/listar_aprendiz.html',contexto)
    else:
        if login and login[3] != "R" and login[3] != "I":
            messages.warning(request, "Uste no está autorizado para éste módulo...")
            return redirect('territorio:index')
        else:
            messages.warning(request, "Debe iniciar sesión primero...")
            return redirect('territorio:loginFormulario')
    
def aprendicesBuscar(request):
    if request.method == "POST":
        
        from django.db.models import Q
        
        q = Aprendiz.objects.filter(
            Q(nombre__icontains = request.POST["dato"]) | 
            Q(apellido__icontains = request.POST["dato"]) | 
            Q(cedula__icontains = request.POST["dato"])
        )
        
        pag = Paginator(q, 4)   #cinco registros por página
        page_number = request.GET.get('page')
        
        #sobreescribo el query
        q = pag.get_page(page_number)
        
        contexto = {'page_obj': q, "dato_buscado": request.POST["dato"]}

        return render(request,'territorio/aprendices/listar_aprendiz_ajax.html',contexto)
    else:
        messages.warning(request, "Usted no envió datos...")
        return redirect('territorio:aprendices')

def aprendicesFormulario(request):
    return render(request, 'territorio/aprendices/crear_aprendiz.html') 

def aprendicesGuardar(request):
    try:
        if request.method == "POST":
            q = Aprendiz(
                cedula = request.POST["cedula"],
                nombre = request.POST["nombre"],
                apellido = request.POST["apellido"],
                fecha_nacimiento = request.POST["fecha_nacimiento"],
            )
            q.save()
            
            messages.success(request, "Aprendiz guardado correctemente!")
            return redirect('territorio:aprendices')
        else:
            messages.warning(request, "Usted no envió datos...")
            return redirect('territorio:aprendices')
    except Exception as e:
        messages.error(request, "Error: " + str(e))
        return redirect('territorio:aprendices')
        

def aprendicesEliminar(request,id):
    try:
        a = Aprendiz.objects.get(pk = id)
        a.delete()
        return HttpResponseRedirect(reverse('territorio:aprendices'))
    except Aprendiz.DoesNotExist:
        return HttpResponse('ERROR: Aprendiz no existe')
    except Exception as e:
        return HttpResponse(f'error: {e}')


def aprendizFormularioEditar(request, id):
    a = Aprendiz.objects.get(pk = id)
    contexto = { "datos": a }
    
    return render(request, 'territorio/aprendices/editar_aprendiz.html', contexto)


def actualizarAprendiz(request):
    try:
        if request.method == "POST":
            a = Aprendiz.objects.get(pk = request.POST["id"])
            
            a.cedula = request.POST["cedula"]
            a.nombre = request.POST["nombre"]
            a.apellido = request.POST["apellido"]
            a.fecha_nacimiento = request.POST["fecha_nacimiento"]
            
            a.save()
            
            messages.success(request, "Aprendiz actualizado correctemente!")
            return redirect('territorio:aprendices')
        else:
            messages.warning(request, "Usted no envió datos...")
            return redirect('territorio:aprendices')
    except Exception as e:
        messages.error(request, "Error: " + str(e))
        return redirect('territorio:aprendices')
     

def monitorias(request):
    q = Monitoria.objects.all()
    contexto = {'datos': q}
    return render(request,'territorio/monitorias/listar_monitorias.html',contexto)

def monitoriasFormulario(request):
    q = Aprendiz.objects.all()
    contexto = {'datos':q}
    return render(request, 'territorio/monitorias/crear_monitorias.html',contexto) 

def monitoriasGuardar(request):
    
    try:
        a = Aprendiz.objects.get(pk = request.POST["aprendiz"])
        
        q = Monitoria(
            cat = request.POST["cat"],
            aprendiz = a,
            fecha_inicio = request.POST["fecha_inicio"],
            fecha_final = request.POST["fecha_final"],
        )
        q.save()
        #return HttpResponse("Monitoria guardada correctemente! <br/> <a href='../monitorias/'>Listar Monitorias</a> ")
        return HttpResponseRedirect(reverse('territorio:monitorias'))
    except Exception as e:
         return HttpResponse("Error: " + str(e))
    
def monitoriasEliminar(request,id):
    try:
        a = Monitoria.objects.get(pk = id)
        a.delete()
        return HttpResponseRedirect(reverse('territorio:monitorias'))
    except Aprendiz.DoesNotExist:
        return HttpResponse('ERROR: Monitoria no existe')
    except Exception as e:
        return HttpResponse(f'error: {e}')

def actividades(request):
    q = Actividades.objects.all()
    contexto = {'datos': q}
    return render(request,'territorio/actividades/listar_actividades.html',contexto)


def actividadesFormulario(request):
    q = Monitoria.objects.all()
    contexto = {'datos':q}
    return render(request, 'territorio/actividades/crear_actividades.html',contexto) 


def actividadesGuardar(request):
    
    try:
        a = Monitoria.objects.get(pk = request.POST["monitoria"])
        
        q = Actividades(
            monitoria = a,
            actividad = request.POST["actividad"],
            observaciones = request.POST["observaciones"],
            fecha = request.POST["fecha"],
        )
        q.save()
        return HttpResponseRedirect(reverse('territorio:actividades'))
    except Exception as e:
         return HttpResponse("Error: " + str(e))

def actividadesEliminar(request,id):
    try:
        a = Actividades.objects.get(pk = id)
        a.delete()
        return HttpResponseRedirect(reverse('territorio:actividades'))
    except Aprendiz.DoesNotExist:
        return HttpResponse('ERROR: Actividad no existe')
    except Exception as e:
        return HttpResponse(f'error: {e}')


def usuarios(request):
    login = request.session.get('logueo', False)
    if login and login[3] == "R":
        q = Usuario.objects.all()
        
        pag = Paginator(q, 4)   #cinco registros por página
        page_number = request.GET.get('page')
        
        #sobreescribo el query
        q = pag.get_page(page_number)
        
        contexto = {'page_obj': q}

        return render(request,'territorio/usuarios/listar_usuarios.html',contexto)
    else:
        if login and login[3] != "R":
            messages.warning(request, "Uste no está autorizado para éste módulo...")
            return redirect('territorio:index')
        else:
            messages.warning(request, "Debe iniciar sesión primero...")
            return redirect('territorio:loginFormulario')
    
def usuariosBuscar(request):
    if request.method == "POST":
        
        from django.db.models import Q
        
        q = Usuario.objects.filter(
            Q(nombre__icontains = request.POST["dato"]) | 
            Q(apellido__icontains = request.POST["dato"]) | 
            Q(usuario__icontains = request.POST["dato"]) |
            Q(rol__icontains = request.POST["dato"])
        )
        
        pag = Paginator(q, 4)   #cinco registros por página
        page_number = request.GET.get('page')
        
        #sobreescribo el query
        q = pag.get_page(page_number)
        
        contexto = {'page_obj': q, "dato_buscado": request.POST["dato"]}

        return render(request,'territorio/usuarios/listar_usuarios_ajax.html',contexto)
    else:
        messages.warning(request, "Usted no envió datos...")
        return redirect('territorio:usuarios')

def usuariosFormulario(request):
    return render(request, 'territorio/usuarios/crear_usuarios.html') 

def usuariosGuardar(request):
    try:
        if request.method == "POST":
            if request.FILES:
                #Crear instancia de File System Storage
                fss = FileSystemStorage()
                #Capturar la foto del formulario
                f = request.FILES["foto"]
                #Cargar archivo al servidor
                file = fss.save("territorio/fotos/" + f.name, f)
            else:
                file = "territorio/fotos/default.png"
            
            q = Usuario(
                nombre = request.POST["nombre"],
                apellido = request.POST["apellido"],
                correo = request.POST["correo"],
                usuario = request.POST["usuario"],
                password = claveEncriptada(request.POST["password"]),
                rol = request.POST["rol"],
                foto = file
            )
            q.save()
            
            messages.success(request, "Usuario guardado correctemente!")
            return redirect('territorio:usuarios')
        else:
            messages.warning(request, "Usted no envió datos...")
            return redirect('territorio:usuarios')
    except Exception as e:
        messages.error(request, "Error: " + str(e))
        return redirect('territorio:usuarios')
        

def usuariosEliminar(request,id):
    try:
        a = Usuario.objects.get(pk = id)
        #primero eliminar la foto y luego al usuario
        
        ruta_foto = str(BASE_DIR) + str(a.foto.url)
        #Averiguar si la ruta es válida....
        if path.exists(ruta_foto):
            #Borramos la foto
            if a.foto.url != "/uploads/territorio/fotos/default.png":
                remove(ruta_foto)
        else:
            raise Exception("La foto no existe o no se encuentra.")
        
        #---------
        a.delete()
        messages.success(request, "Usuario eliminado correctamente!.")
    except Usuario.DoesNotExist:
        messages.error(request, "ERROR: Usuario no existe")
    except Exception as e:
        messages.error(request, f'No se pudo eliminar el usuario: {e}')
        
    return redirect('territorio:usuarios')

def usuariosFormularioEditar(request, id):
    a = Usuario.objects.get(pk = id)
    contexto = { "datos": a }
    
    return render(request, 'territorio/usuarios/editar_usuarios.html', contexto)


def usuariosActualizar(request):
    try:
        if request.method == "POST":
            a = Usuario.objects.get(pk = request.POST["id"])
            
            if request.FILES:
                #Eliminar foto anterior
                ruta_foto = str(BASE_DIR) + str(a.foto.url)
                if path.exists(ruta_foto):
                    if a.foto.url != "/uploads/territorio/fotos/default.png":
                        remove(ruta_foto)
                else:
                    raise Exception("La foto no existe o no se encuentra.")
                
                #Guardar foto nueva
                fss = FileSystemStorage()
                f = request.FILES["foto"]
                file = fss.save("territorio/fotos/" + f.name, f)
                
                a.foto = file
            else:
                print("El usuario no seleccionó foto nueva")

            
            a.nombre = request.POST["nombre"]
            a.apellido = request.POST["apellido"]
            a.correo = request.POST["correo"]
            a.usuario = request.POST["usuario"]
            a.password = claveEncriptada(request.POST["password"])
            a.rol = request.POST["rol"]
            
            
            a.save()
            
            messages.success(request, "Usuario actualizado correctemente!")
            return redirect('territorio:usuarios')
        else:
            messages.warning(request, "Usted no envió datos...")
            return redirect('territorio:usuarios')
    except Exception as e:
        messages.error(request, "Error: " + str(e))
        return redirect('territorio:usuarios')
  