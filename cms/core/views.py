from pyexpat.errors import messages
from django.shortcuts import render, HttpResponse,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol,Rol
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import PermissionRequiredMixin
from pathlib import Path
from lxml.html.diff import htmldiff
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView
from .models import Categoria
from .models import Contenido,HistorialContenido
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

class CrearContenido(CreateView):
    """
    La clase creacontenido utiliza el view de django CreateView, este view nos permite rellenar datos para un modelo
    en este caso para el modelo contenido, utilizamos el template crear_contenido
    """
    model= Contenido
    template_name= 'crear_contenido.html'
    fields= '__all__'
    model = Contenido
    fields = ['titulo', 'categoria', 'resumen', 'imagen', 'cuerpo','razon']  # excluye 'estado'
    def form_valid(self, form):
        form.instance.estado = 'B'  # Establece el estado inicial a 'B'
        form.instance.autor = UsuarioRol.objects.get(username=self.request.user.username)

        response = super().form_valid(form)

        if "guardar_borrador" in self.request.POST:
            # Si se presionó el botón "Guardar borrador", no cambies nada
            self.object.save()

            # Crea una instancia de HistorialContenido con la instancia de Contenido
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"Se Creo el contenido con ID {self.object.id}, Con el Titulo {self.object.titulo} por el autor {self.object.autor.username}."
            )
            nuevo_cambio.save()
            return redirect('vista_autor')
        elif "enviar_editor" in self.request.POST:
            # si se presionó el botón "Enviar a editor", cambia el estado a 'E'
            self.object.estado = 'E'
            self.object.save()
            return redirect('vista_autor')

        return response
    
class EditarContenido(UpdateView):
    model = Contenido
    template_name = 'edit_cont.html'
    fields = ['titulo', 'autor', 'categoria', 'resumen', 'imagen', 'cuerpo','razon']
    def form_valid(self, form):
        form.instance.estado = 'B'  # establece el estado inicial a 'B'
        response = super().form_valid(form)
        if "guardar_borrador" in self.request.POST:
            # si se presionó el botón "Guardar borrador", no cambies nada
            self.object.save()
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El Autor con ID {self.object.autor.id},con username {self.object.autor.username},Edito el contenido  Con el Titulo {self.object.titulo}."
            )
            nuevo_cambio.save()
            return redirect('vista_autor')
        return response
    


class EditarContenidoEditor(UpdateView):
    model = Contenido
    template_name = 'editar_contenido_editor.html'
    fields = ['titulo', 'categoria', 'resumen', 'imagen', 'cuerpo','razon']
    def form_valid(self, form):
        form.instance.estado = 'E'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "cancelar" in self.request.POST:
            return redirect('edicion')
        else:
            """
            Comprueba las ediciones realizadas, construye y envia el email de notificacion
            """
            cambios = None
            cambios_cuerpo = None
            if form.has_changed():
                cambios = ', '.join(form.changed_data)
                t1 = form["cuerpo"].initial
                t2 = self.object.cuerpo
                if t1 and t2 and (t1 != t2):
                    cambios_cuerpo = htmldiff(t1, t2) 
             
            mensaje_edicion = render_to_string("email-notifs/email_edicion.html",
                                                    {'nombre_editor': self.request.user.username,
                                                    'titulo_contenido': form['titulo'].initial,
                                                    'contenido_cambiado': cambios,
                                                    'cambios_cuerpo': cambios_cuerpo})
            
            # Solo envia el email de edicion si de verdad se modifico el contenido
            if cambios or cambios_cuerpo:
                send_mail(subject="Contenido editado", message=f"Su contenido {form['titulo'].initial} fue editado",
                            from_email=None,
                                recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                                html_message=mensaje_edicion)
            
        return response    

class RechazarContenidoEditor(UpdateView):
    model = Contenido
    template_name = 'rechazo.html'
    fields = ['razon']
    def form_valid(self, form):
        form.instance.estado = 'r'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "cancelar" in self.request.POST:
            return redirect('edicion')
        elif "enviar_autor" in self.request.POST:
            self.object.estado = 'r'
            self.object.ultimo_editor=self.request.user.username
            self.object.save()
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El contenido con el Titulo {self.object.titulo} fue rechazado por el editor {self.object.ultimo_editor}. El contenido pasa a estado 'Rechazado(r)'."
            )
            nuevo_cambio.save()  
            mensaje_edicion = render_to_string("email-notifs/email_rechazo.html",
                                            {'nombre': self.request.user.username,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon})
        
           
            send_mail(subject="Contenido rechazado", message=f"Su contenido {self.object.titulo} fue rechazado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('edicion')
            
        return response    
    


class RechazarContenidoPublicador(UpdateView):
    model = Contenido
    template_name = 'rechazo_publicador.html'
    fields = ['razon']
    def form_valid(self, form):
        form.instance.estado = 'r'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "enviar_autor" in self.request.POST:
            self.object.estado = 'r'
            self.object.publicador= UsuarioRol.objects.get(username=self.request.user.username)
            self.object.ultimo_publicador=self.request.user.username
            self.object.save()

            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El contenido con el Titulo {self.object.titulo} fue rechazado por el publicador {self.object.ultimo_publicador}. El contenido pasa a estado 'Rechazado(r)'."
            )
            nuevo_cambio.save()
            mensaje_edicion = render_to_string("email-notifs/email_rechazo.html",
                                            {'nombre': self.request.user.username,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon})
        
           
            send_mail(subject="Contenido rechazado", message=f"Su contenido {self.object.titulo} fue rechazado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            
            
            return redirect('Publicador')
            
        return response 

class EnviarContenidoAutor(UpdateView):
    model = Contenido
    template_name = 'enviar_contenido_autor.html'
    fields = ['razon']
    def form_valid(self, form):
        form.instance.estado = 'B'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "enviar_editor" in self.request.POST:
            self.object.estado = 'E'
            self.object.save()
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"Se envio el contenido el con el Titulo {self.object.titulo} por el autor {self.object.autor.username}, a edicion. El contenido pasa a esto 'En Edicion'"
            )
            nuevo_cambio.save()
            mensaje_edicion = render_to_string("email-notifs/email_notificacion_enviar_edicion.html",
                                            {'nombre': self.request.user.username,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon})
        
           
            send_mail(subject="Contenido Enviado a revision", message=f"Su contenido {self.object.titulo} fue enviado a edicion",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('ContenidosBorrador')
            
        return response     
    
class EnviarContenidoEditor(UpdateView):
    model = Contenido
    template_name = 'enviar_contenido_editor.html'
    fields = ['razon']
    def form_valid(self, form):
        form.instance.estado = 'E'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "enviar_publicador" in self.request.POST:
            self.object.estado = 'R'
            self.object.editor= UsuarioRol.objects.get(username=self.request.user.username)
            self.object.ultimo_editor= self.request.user.username
            self.object.save()
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"Se envio el contenido el con el Titulo {self.object.titulo} por el autor {self.object.autor.username}, a publicacion. El contenido pasa a estado 'En Revision'. El Editor que envio a publicacion fue : {self.object.ultimo_editor}"
            )
            nuevo_cambio.save()
            mensaje_edicion = render_to_string("email-notifs/email_notificacion_enviar_publicacion.html",
                                            {'nombre': self.request.user.username,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon})
        
           
            send_mail(subject="Contenido Enviado a un publicador para su revision", message=f"Su contenido {self.object.titulo} fue enviado a revision para ser publicado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            
            mensaje_edicion = render_to_string("email-notifs/email_notificacion_editor_a_publicar.html",
                                            {'nombre_editor': self.request.user.username,
                                            'nombre_autor': self.object.autor,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon})
        
           
            send_mail(subject="Contenido Enviado a un publicador para su revision", message=f"El contenido {self.object.titulo} realizado por {self.object.autor_id} fue editado por ustes y enviado para su revision antes de ser publicado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(username=self.request.user.username).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('edicion')
            
        return response   
@never_cache
def vista_MenuPrincipal(request):
    """
    Fecha documentacion: 28/08/2023
    Esta vista nos permite ingresar al template del menu principal, le pasamos como contextos 
    los datos de usuario y de usuariorol en caso de que ya inicio sesion
    autenticado=User.is_authenticated
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
        }
    else:
        context={
            'autenticado': autenticado
        }    
    print("Usuario: ",autenticado)

    Fecha de documentacion: 07-09-2023
    Se modifico el fetch de contenidos para ignorar usuarios inactivos
    autores_activos= UsuarioRol.objects.filter(usuario_activo=True)
    contenidos=Contenido.objects.filter(autor__in=autores_activos)
    primeros_contenidos = contenidos[:6]
    """
    autenticado=User.is_authenticated
    categorias= Categoria.objects.filter(activo=True)
    autores_activos= UsuarioRol.objects.filter(usuario_activo=True) # Solo mostrar contenidos de autores activos
    contenidos=Contenido.objects.filter(autor__in=autores_activos)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    primeros_contenidos = contenidos.filter(estado='P')[:10]

    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores
        }
    else:
        context={
            'autenticado': autenticado,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores
        }    
    print("Usuario: ",autenticado)
    return render(request, 'crear/main.html',context )
@login_required(login_url="/login")
def vista_trabajador(request):
    """
    Fecha documentacion: 28/08/2023
    Nos permite redigir al usuario al template de trabajores, le pasamos como datos 
    usuario_rol debido que se utiliza en el html para sbaer que botones mostrar al usuario 
    de acuerdo a su rol
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 
    """
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 



class CustomPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Fecha documentacion: 06/09/2023
    Permite comprobar permisos personalizados del usuario al ser heredada en vistas basadas en clases
    """
    def has_permission(self) -> bool:
        perms = self.get_permission_required()
        usuario_rol = UsuarioRol.objects.get(username=self.request.user.username)
        tiene_permiso = True
        for perm in perms:
            tiene_permiso = tiene_permiso and usuario_rol.has_perm(perm)
        return tiene_permiso
class VistaArticulos(DetailView):
    """Utilizamos esta vista para ir a un contenido, en la misma nos redirecciona al template de contenidos,\
    donde se ve el cuerpo del contenido, imagenes, autor etc"""
    model = Contenido
    template_name='articulo_detallado.html'

class VistaArticulosEditor(DetailView):
    model = Contenido
    template_name='articulo_detallado_edicion.html'

class VistaArticulosRevision(DetailView):
    model = Contenido
    template_name='articulo_detallado_revision.html'



   
class VistaContenidos(ListView):
    """
    Esta vista al ser un LisstView utilizamos para listar los contenidos, al pasarle como modelos el contennido, 
    dentro del html podemos usar un object list para ver todos los contenidos de nuestro sistema
    """
    model= Contenido
    template_name='Contenidos.html'

@login_required(login_url="/login")
def categoria(request,nombre):

    """
    Fecha documentacion: 08/09/2023
    Esta vista nos permite ingresar a una vista personalizada por categorias, es decir ir a un lugar donde todos
    los contenidos pertenezcan a esa categoria
    autenticado=User.is_authenticated
    categoria= get_object_or_404(Categoria,nombre=nombre)
    contenidos=Contenido.objects.filter(categoria_id=categoria.id)
    context = {
        'categoria': categoria,
        'contenidos': contenidos
        
    }
    return render(request,'categoria.html',context)
    """

    categoria= get_object_or_404(Categoria,nombre=nombre)
    contenidos=Contenido.objects.filter(categoria_id=categoria.id)
    context = {
        'categoria': categoria,
        'contenidos': contenidos
        
    }
    return render(request,'categoria.html',context)

@login_required(login_url="/login")
def crear_categoria(request):
    """
    Fecha documentacion: 08/09/2023
    Esta vista nos permite crear nuevas categorias para nuestro sitio.
    Una vez creada noe redirige al sitio del administrador
      if request.method == 'POST':
        nombre1=request.POST['nombre']
        moderado=request.POST['moderada']
        categoria=Categoria(nombre=nombre1,moderada=moderado)
        categoria.save()
        return redirect('Administrador')
        return render(request,'crear_cat.html')
    """
    if request.method == 'POST':
        nombre1=request.POST['nombre']
        moderado=request.POST['moderada']
        categoria=Categoria(nombre=nombre1,moderada=moderado)
        categoria.save()
        return redirect('Administrador')
    return render(request,'crear_cat.html')
@login_required(login_url="/login")
def desactivar_categoria(request):
    """
        Fecha documentacion: 08/09/2023
        Esta vista nos permite desactivar  categorias existentes en nuestro sitio.
        Una vez desactivada ya no aparecera en elmen, pero sus contenidos seguiran siendo visibles en el general
        if request.method == 'POST':
        id_categoria= request.POST['id_categoria']
            categoria=Categoria.objects.get(id=id_categoria)
            categoria.activo=False
            categoria.save()
            return redirect('Administrador')

        return render(request, 'desactivar_cat.html')
    """
    if request.method == 'POST':
        id_categoria= request.POST['id_categoria']
        categoria=Categoria.objects.get(id=id_categoria)
        categoria.activo=False
        categoria.save()
        return redirect('Administrador')

    return render(request, 'desactivar_cat.html')


@login_required(login_url="/login")
def vista_roles(request):
    """
    Documentado el 08/09/2023
    Esta vista nos devuelve un template donde podremos gestionarroles de nuestros usuarios activos
    """
    return render(request,'gestion_roles.html')

@login_required(login_url="/login")
def asignar_rol(request):
    """
    Documentado el 08/09/2023

    Esta vista nos permitira asignar un rol a un usuario activo.
    La vista desplegara una lista de usuarios y alli al elegir un usuario se desplegara sus roles actuales
    y en la otra lista de asignacion apareceran todos los roles qe este usuario aun no dispone

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.add(rol)
        return redirect('asignacion')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        roles = Rol.objects.all()
        usuario_seleccionado = None
        roles_usuario = []
        roles_disponibles = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
            roles_disponibles = Rol.objects.exclude(id__in=roles_usuario.values_list('id', flat=True))
        context = {
            'usuarios': usuarios,
            'roles': roles,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
            'roles_disponibles': roles_disponibles
        }
        return render(request, 'asignar_rol.html', context)
    """
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.add(rol)
        return redirect('asignacion')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        roles = Rol.objects.all()
        usuario_seleccionado = None
        roles_usuario = []
        roles_disponibles = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
            roles_disponibles = Rol.objects.exclude(id__in=roles_usuario.values_list('id', flat=True))
        context = {
            'usuarios': usuarios,
            'roles': roles,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
            'roles_disponibles': roles_disponibles
        }
        return render(request, 'asignar_rol.html', context)
    
@login_required(login_url="/login")    
def remover_rol(request):
    """
    Documentado el 08/09/2023

    Este metodo es algo parecido al asignar, solo que al escofer un usuario, veremos los roles que podemos quitarle.
    y al elegir uno le eliminareos ese rol.
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.remove(rol)
        return redirect('desasignar')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        usuario_seleccionado = None
        roles_usuario = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
        context = {
            'usuarios': usuarios,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
        }
        return render(request, 'desasignar_rol.html', context)
      """
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.remove(rol)
        return redirect('desasignar')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        usuario_seleccionado = None
        roles_usuario = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
        context = {
            'usuarios': usuarios,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
        }
        return render(request, 'desasignar_rol.html', context)

    

    """
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.remove(rol)
        return redirect('desasignar')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        usuario_seleccionado = None
        roles_usuario = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
        context = {
            'usuarios': usuarios,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
        }
        return render(request, 'desasignar_rol.html', context)
    """

@login_required(login_url="/login")
def vista_editor(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'vista_editor.html',context)

@login_required(login_url="/login")
def vista_edicion(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'editar_contenidos.html',context)

@login_required(login_url="/login")
def vista_publicador(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'contenidos_revision.html',context)

@login_required(login_url="/login")
def vista_autor(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'vista_autor.html',context)

@login_required(login_url="/login")
def vista_mis_contenidos_borrador(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'mis_contenidos_borrador.html',context)

  
@login_required(login_url="/login")
def vista_mis_contenidos_rechazados(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'mis_contenidos_rechazados.html',context)

  

@login_required(login_url="/login")
def vista_mis_contenidos_publicados(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'mis_contenidos_publicados.html',context)

    

@login_required(login_url="/login")
def publicar_contenido(request,contenido_id):
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.estado = 'P'
    contenido.publicador= UsuarioRol.objects.get(username=request.user.username)
    contenido.ultimo_publicador=request.user.username
    contenido.fecha_publicacion = timezone.now().date()
    # Guarda el objeto de contenido
    contenido.save()
    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"Se publico el contenido con el Titulo {contenido.titulo} por el autor {contenido.autor.username}. El contenido pasa a estado 'Publicado'. El Publicador que acepto la publicacion fue : {contenido.ultimo_publicador}"
            )
    nuevo_cambio.save()
    mensaje_edicion = render_to_string("email-notifs/email_notificacion_enviar_publicacion.html",
                                            {'nombre': request.user.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
        
    send_mail(subject="Contenido Publicado en la pagina", message=f"Su contenido {contenido.titulo} fue publicado en la pagina",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_publicador.html",
                                            {'nombre_publicador': request.user.username,
                                            'nombre_editor':contenido.ultimo_editor,
                                            'nombre_autor':contenido.autor_id,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
        
    send_mail(subject="Contenido Publicado en la pagina", message=f"Su contenido {contenido.titulo} fue publicado en la pagina",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(username=contenido.publicador.username).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    # Redirige al usuario a la vista del editor
    return redirect('Publicador')

@login_required(login_url="/login")
def inactivar_contenido(request,contenido_id):
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.fecha_publicacion = None
    contenido.estado = 'I'
   
    # Guarda el objeto de contenido
    contenido.save()
    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El contenido con el Titulo {contenido.titulo} fue inactivado por su autor {contenido.autor.username}. El contenido pasa a estado 'Inactivo(I)'."
            )
    nuevo_cambio.save()
    mensaje_edicion = render_to_string("email-notifs/email_notificacion_inactivar_autor.html",
                                            {
                                            'nombre_editor':contenido.ultimo_editor,
                                            'nombre_autor':contenido.autor_id,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
    

    send_mail(subject="Contenido ha pasado al estado inactivo", message=f"Su contenido {contenido.titulo} fue bajado del sitio y se encuentra en estado inactivo",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_inactivar_publicador.html",
                                            {
                                            'nombre_editor':contenido.editor.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
    

    send_mail(subject="El autor de un contenido ha dado de baja su contenido", message=f"El contenido {contenido.titulo} que publicaste, ha sido bajado por su autor {contenido.autor.username}",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(username=contenido.publicador.username).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    
    # Redirige al usuario a la vista del editor
    return redirect('ContenidosPublicados')
@login_required(login_url="/login")
def aceptar_rechazo_contenido(request,contenido_id):
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)

    contenido.estado = 'B'
    contenido.razon_rechazo=' '
    # Guarda el objeto de contenido
    contenido.save()
    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El autor {contenido.autor.username} Acepto el rechazo del contenido con el Titulo {contenido.titulo} que fue rechazado por el publicador {contenido.ultimo_publicador}. El contenido pasa a estado 'Borrador(B)'."
    )
    nuevo_cambio.save()


    mensaje_edicion = render_to_string("email-notifs/email_notificacion_aceptar_rechazo_autor.html",
                                            {
                                            'nombre_publicador':contenido.publicador.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
    
    send_mail(subject="Haz aceptado el rechazo de un contenido", message=f"Se acepto el rechazo de  {contenido.titulo}",
                from_email=None,
                    recipient_list=[contenido.autor.email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    
    
   
    
       
    # Redirige al usuario a la vista del editor
    return redirect('ContenidosRechazados')

@login_required(login_url="/login")
def rechazar_contenido(request,contenido_id):
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.publicador= UsuarioRol.objects.get(username=request.user.username)
    contenido.ultimo_publicador=request.user.username
    contenido.estado = 'r'

    # Guarda el objeto de contenido
    contenido.save()

    # Redirige al usuario a la vista del editor
    return redirect('Publicador')
@login_required(login_url="/login")
def publicador(request):
   return render(request,'vista_publicador.html')

@login_required(login_url="/login")
def contenidos_inactivos(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'contenidos_inactivos.html',context)     
@login_required(login_url="/login")
def reactivar_contenido(request,contenido_id):
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.estado = 'P'
    contenido.publicador= UsuarioRol.objects.get(username=request.user.username)
    contenido.ultimo_publicador=request.user.username
    # Guarda el objeto de contenido
    contenido.save()
    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El contenido con el Titulo {contenido.titulo} fue reactivado por el publicador {contenido.ultimo_publicador}. El contenido pasa a estado 'Publicado(P)'."
    )
    nuevo_cambio.save()
    mensaje_edicion = render_to_string("email-notifs/email_notificacion_reactivar_contenido_autor.html",
                                            {
                                            'nombre_publicador':contenido.publicador.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
    
    send_mail(subject="Se ha republicado  un contenido", message=f"Se reactivo  el contenido {contenido.titulo} de tu autoria, el publicador que realizo esta accion fue{contenido.publicador.username}",
                from_email=None,
                    recipient_list=[contenido.autor.email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_reactivar_contenido_publicador.html",
                                            {
                                            'nombre_publicador':contenido.publicador.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon})
    
    send_mail(subject="Haz republicado  un contenido", message=f"Se reactivo  el contenido {contenido.titulo} de tu autoria, el publicador que realizo esta accion fue{contenido.publicador.username}",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(username=contenido.publicador.username).email, 'is2cmseq03@gmail.com'],
                    html_message=mensaje_edicion)
    # Redirige al usuario a la vista del editor
    return redirect('contenidos-inactivos')
@login_required(login_url="/login")
def tabla_kanban(request):
    categorias= Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores= UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicador=UsuarioRol.objects.filter(roles__nombre__contains='Publicador')
    contenido_borrador=Contenido.objects.filter(estado='B')
    contenidos_inactivos = Contenido.objects.filter(estado='I')
    contenidos_en_revision = Contenido.objects.filter(estado='R')
    contenidos_publicados = Contenido.objects.filter(estado='P')
    contenidos_en_edicion = Contenido.objects.filter(estado='E')
    context = {
        'categorias':categorias,
        'autores':autores,
        'editores':editores,
        'publicadores':publicador,
        'contenidos_borrador': contenido_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion':contenidos_en_edicion,
    }

    return render(request, 'Tabla/tablakanban.html', context)
@login_required(login_url="/login")
def tabla_kanbangeneral(request):
    categorias= Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores= UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicador=UsuarioRol.objects.filter(roles__nombre__contains='Publicador')
    contenido_borrador=Contenido.objects.filter(estado='B')
    contenidos_inactivos = Contenido.objects.filter(estado='I')
    contenidos_en_revision = Contenido.objects.filter(estado='R')
    contenidos_publicados = Contenido.objects.filter(estado='P')
    contenidos_en_edicion = Contenido.objects.filter(estado='E')
    context = {
        'categorias':categorias,
        'autores':autores,
        'editores':editores,
        'publicadores':publicador,
        'contenidos_borrador': contenido_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion':contenidos_en_edicion,
    }
    return render(request, 'Tabla/tablakanbangeneral.html', context)
@login_required(login_url="/login")
def buscar_tabla(request):
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria')
    autor = request.GET.get('autor')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Inicializar el queryset con todos los contenidos
    contenidos = Contenido.objects.all()

    # Si hay un término de búsqueda, filtrar por el campo correspondiente
    if q:
        contenidos = contenidos.filter(titulo__icontains=q)

    # Si hay una categoría seleccionada, filtrar por el campo categoria
    if categoria:
        contenidos = contenidos.filter(categoria__nombre=categoria)

    # Si hay un autor seleccionado, filtrar por el campo autor
    if autor:
        contenidos = contenidos.filter(autor__username=autor)

    # Si se proporciona fecha de inicio pero no fecha de fin, filtrar por el campo fecha_publicacion desde la fecha de inicio
    if fecha_inicio and not fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__gte=fecha_inicio)

    # Si se proporciona fecha de fin pero no fecha de inicio, filtrar por el campo fecha_publicacion hasta la fecha de fin
    elif fecha_fin and not fecha_inicio:
        contenidos = contenidos.filter(fecha_publicacion__lte=fecha_fin)

    # Si se proporcionan fechas de inicio y fin, filtrar por el campo fecha_publicacion en el rango de esas fechas
    elif fecha_inicio and fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__range=[fecha_inicio, fecha_fin])
    categorias= Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores= UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicador=UsuarioRol.objects.filter(roles__nombre__contains='Publicador')
    contenido_borrador=contenidos.filter(estado='B')
    contenidos_inactivos = contenidos.filter(estado='I')
    contenidos_en_revision = contenidos.filter(estado='R')
    contenidos_publicados = contenidos.filter(estado='P')
    contenidos_en_edicion = contenidos.filter(estado='E')
    context = {
        'categorias':categorias,
        'autores':autores,
        'editores':editores,
        'publicadores':publicador,
        'contenidos_borrador': contenido_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion':contenidos_en_edicion,
    }
    return render(request, 'Tabla/tablakanbangeneral.html', context)
def buscar_tabla_autor(request):
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria')
    autor = request.GET.get('autor')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Inicializar el queryset con todos los contenidos
    contenidos = Contenido.objects.all()

    # Si hay un término de búsqueda, filtrar por el campo correspondiente
    if q:
        contenidos = contenidos.filter(titulo__icontains=q)

    # Si hay una categoría seleccionada, filtrar por el campo categoria
    if categoria:
        contenidos = contenidos.filter(categoria__nombre=categoria)

    # Si hay un autor seleccionado, filtrar por el campo autor
    if autor:
        contenidos = contenidos.filter(autor__username=autor)

    # Si se proporciona fecha de inicio pero no fecha de fin, filtrar por el campo fecha_publicacion desde la fecha de inicio
    if fecha_inicio and not fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__gte=fecha_inicio)

    # Si se proporciona fecha de fin pero no fecha de inicio, filtrar por el campo fecha_publicacion hasta la fecha de fin
    elif fecha_fin and not fecha_inicio:
        contenidos = contenidos.filter(fecha_publicacion__lte=fecha_fin)

    # Si se proporcionan fechas de inicio y fin, filtrar por el campo fecha_publicacion en el rango de esas fechas
    elif fecha_inicio and fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__range=[fecha_inicio, fecha_fin])
    categorias= Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores= UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicador=UsuarioRol.objects.filter(roles__nombre__contains='Publicador')
    contenido_borrador=contenidos.filter(estado='B')
    contenidos_inactivos = contenidos.filter(estado='I')
    contenidos_en_revision = contenidos.filter(estado='R')
    contenidos_publicados = contenidos.filter(estado='P')
    contenidos_en_edicion = contenidos.filter(estado='E')
    context = {
        'categorias':categorias,
        'autores':autores,
        'editores':editores,
        'publicadores':publicador,
        'contenidos_borrador': contenido_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion':contenidos_en_edicion,
    }
    return render(request, 'Tabla/tablakanban.html', context)
def historial_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)  # Obtener la instancia de Contenido por su ID
    historial_prueba = HistorialContenido.objects.filter(contenido=contenido)
    context = {
        'historial_prueba': historial_prueba,
        'contenido': contenido  # Pasar la instancia de Contenido al contexto si es necesario
    }
    return render(request, 'historial_contenido.html', context)
