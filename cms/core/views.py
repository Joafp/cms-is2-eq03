from pyexpat.errors import messages
from typing import Any
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
from decimal import Decimal
from django.db.models import Sum
from .models import Categoria
from .models import Likes
from .models import Contenido,HistorialContenido,VersionesContenido,Comentario
from .models import Contenido,HistorialContenido,VersionesContenido,Comentario,Calificacion
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.paginator import Paginator, Page
from .forms import CrearContenidoForm
from django.db.models import Avg
from django.http import JsonResponse
import qrcode
from django.http import HttpResponse

class CrearContenido(CreateView):
    """
    La clase creacontenido utiliza el view de django CreateView, este view nos permite rellenar datos para un modelo
    en este caso para el modelo contenido, utilizamos el template crear_contenido
    """
    form_class= CrearContenidoForm
    template_name= 'crear_contenido.html'
    
    def form_valid(self, form):
        form.instance.estado = 'B'  # establece el estado inicial a 'B'
        response = super(CrearContenido, self).form_valid(form)
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
    
    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['autor'] = UsuarioRol.objects.get(username=self.request.user.username)
        return initial
    
class EditarContenido(UpdateView):
    """
    La clase EditarContenido utiliza el view de django UpdateView, este view nos permite updatear los datos para un modelo
    en este caso para el modelo contenido, utilizamos el template crear_contenido.
    Modificamos lo anteriormente cargado cuando creqamos el contenido, nos da la opcion de guardar comom borrador y este crea una nueva version del contenido.
    La opcion de enviar al editor cambia el estado a ´En revision´ y manda a los editores para que estos lo revise
    """
    model=Contenido
    form_class= CrearContenidoForm
    template_name = 'edit_cont.html'

    def form_valid(self, form):
        form.instance.estado = 'B'  # establece el estado inicial a 'B'
        response = super().form_valid(form)
        # if "guardar_borrador" in self.request.POST:
        #     # si se presionó el botón "Guardar borrador", no cambies nada
        #     self.object.save()
        #     nuevo_cambio = HistorialContenido(
        #         contenido=self.object,  # Asigna la instancia de Contenido, no el ID
        #         cambio=f"El Autor con ID {self.object.autor.id},con username {self.object.autor.username},Edito el contenido  Con el Titulo {self.object.titulo}."
        #     )
        #     nuevo_cambio.save()
        #     return redirect('vista_autor')
        # elif "guardar_version" in self.request.POST:
        if "guardar_borrador" in self.request.POST:
            # primero guarda el borrador y luego la version
            numero_version = 1
            ultima_version = VersionesContenido.objects.filter(contenido_base=self.object).order_by('-numero_version')
            if ultima_version.exists():
                numero_version = 1 + ultima_version[0].numero_version
            self.object.save()
            nuevo_cambio = HistorialContenido(
                contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El Autor con ID {self.object.autor.id},con username {self.object.autor.username},Edito el contenido  Con el Titulo {self.object.titulo}Se creo la version {numero_version} del contenido"
            )
            nuevo_cambio.save()
            guardar_version(self.object, numero_version)
            return redirect('ContenidosBorrador')
        elif "enviar_editor" in self.request.POST:
            # si se presionó el botón "Enviar a editor" se guardan los cambios 
            self.object.save()
        return response
    


class EditarContenidoEditor(UpdateView):
    """
    La clase EditarContenidoEditor utiliza el view de django UpdateView, este view nos permite updatear los datos para un modelo
    en este caso para el modelo contenido, utilizamos el template editar_contenido_editor.html.
    Modificamos lo anteriormente cargado cuando el autor creo el contenido, basicamente psi un editor quiere cambiar algo que hizo un autor. Luego si aceptamos enviamos a un publicador
    """
    model=Contenido
    form_class= CrearContenidoForm
    template_name = 'editar_contenido_editor.html'
    
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
                                                    'cambios_cuerpo': cambios_cuerpo,
                                                    'urlhost':self.request.get_host(),
                                                    'contenidopk':self.object.pk})
            
            # Solo envia el email de edicion si de verdad se modifico el contenido
            if cambios or cambios_cuerpo:
                send_mail(subject="Contenido editado", message=f"Su contenido {form['titulo'].initial} fue editado",
                            from_email=None,
                                recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                                html_message=mensaje_edicion)
            
        return response    

class RechazarContenidoEditor(UpdateView):
    """
        La clase RechazarContenidoEditor utiliza el view de django UpdateViewo, utilizamos el template rechazo.html.
        esta clase nos permite cambiar el estado de un contenido en caso de ser rechazado , asi poner ene stado rechazado y que se le notifique al autor de esto.
    
    """
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
                                            'razon': self.object.razon,
                                            'urlhost':self.request.get_host(),
                                                    'contenidopk':self.object.pk})
        
           
            send_mail(subject="Contenido rechazado", message=f"Su contenido {self.object.titulo} fue rechazado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('edicion')
            
        return response    
    


class RechazarContenidoPublicador(UpdateView):
    """
        La clase RechazarContenidoPublicador utiliza el view de django UpdateViewo, utilizamos el template rechazo_publicador.html.
        esta clase nos permite cambiar el estado de un contenido en caso de ser rechazado , asi poner en estado rechazado y que se le notifique al autor de esto.
    
    """
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
                                            'razon': self.object.razon,
                                            'urlhost':self.request.get_host(),
                                                    'contenidopk':self.object.pk})
        
           
            send_mail(subject="Contenido rechazado", message=f"Su contenido {self.object.titulo} fue rechazado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            
            
            return redirect('Publicador')
            
        return response 

class EnviarContenidoAutor(UpdateView):
    """
        ESTA VISTA PERMITE EL AUTOR REMITIR SU CONTENIDO A UN EDITOR. O PUBLICAR DIRECTAMENTE EN CASO DE SER UN AUTOR CHECKEADO PARA PUBLICAR EN  CATEGORIAS NO MODERADAS
    """
    model = Contenido
    template_name = 'enviar_contenido_autor.html'
    fields = ['razon']
    def form_valid(self, form):
        form.instance.estado = 'B'  # establece el estado inicial a 'E'
        response = super().form_valid(form)
        if "enviar_editor" in self.request.POST:
            # Publica directamente si la categoria es no moderada
            if self.object.categoria.moderada == False:
                self.object.ultimo_publicador=self.request.user.username
                self.object.estado = 'P'
                self.object.save()
                mensaje_edicion = render_to_string("email-notifs/email_notificacion_enviar_publicacion.html",
                                                {'nombre': self.request.user.username,
                                                'titulo_contenido': self.object.titulo,
                                                'razon': self.object.razon,
                                                'urlhost':self.request.get_host(),
                                                        'contenidopk':self.object.pk})
            
                send_mail(subject="Contenido Publicado en la pagina", message=f"Su contenido {self.object.titulo} fue publicado en la pagina",
                    from_email=None,
                        recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                        html_message=mensaje_edicion)
        

                mensaje_edicion = render_to_string("email-notifs/email_notificacion_publicador.html",
                                                {'nombre_publicador': self.request.user.username,
                                                'nombre_editor':self.object.ultimo_editor,
                                                'nombre_autor':self.object.autor_id,
                                                'titulo_contenido': self.object.titulo,
                                                'razon': self.object.razon,
                                                'urlhost':self.request.get_host(),
                                                        'contenidopk':self.object.pk})
            
                send_mail(subject="Contenido Publicado en la pagina", message=f"Su contenido {self.object.titulo} fue publicado en la pagina",
                    from_email=None,
                        recipient_list=[UsuarioRol.objects.get(username=self.object.ultimo_publicador).email, 'is2cmseq03@gmail.com', ],
                        html_message=mensaje_edicion)
                # Redirige al usuario a la vista del editor
                return redirect('vista_autor')
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
                                            'razon': self.object.razon,
                                            'urlhost':self.request.get_host(),
                                            'contenidopk':self.object.pk})
        
           
            send_mail(subject="Contenido Enviado a revision", message=f"Su contenido {self.object.titulo} fue enviado a edicion",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('ContenidosBorrador')
            
        return response     
    
class EnviarContenidoEditor(UpdateView):
    """
    Esta vista permite  que un editor remita sun contenido a un publicador para su revision y posterior publicacion, se envian mensajes en el correo electronico al autor para decirle que su contenido ha sido pasado a revision de publicadores.
    """
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
                                            'razon': self.object.razon,
                                            'urlhost':self.request.get_host(),
                                                    'contenidopk':self.object.pk})
        
           
            send_mail(subject="Contenido Enviado a un publicador para su revision", message=f"Su contenido {self.object.titulo} fue enviado a revision para ser publicado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=self.object.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            
            mensaje_edicion = render_to_string("email-notifs/email_notificacion_editor_a_publicar.html",
                                            {'nombre_editor': self.request.user.username,
                                            'nombre_autor': self.object.autor,
                                            'titulo_contenido': self.object.titulo,
                                            'razon': self.object.razon,
                                            'urlhost':self.request.get_host(),
                                                    'contenidopk':self.object.pk})
        
           
            send_mail(subject="Contenido Enviado a un publicador para su revision", message=f"El contenido {self.object.titulo} realizado por {self.object.autor_id} fue editado por ustes y enviado para su revision antes de ser publicado",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(username=self.request.user.username).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)
            
            return redirect('Editar')
            
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
from datetime import datetime
def vista_MenuPrincipal_filtrado(request):
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
      # Obtiene los parámetros de búsqueda del formulario
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')  # Establecer valor predeterminado
    autor = request.GET.get('autor', '')  # Establecer valor predeterminado
    fecha_inicio = request.GET.get('fecha_inicio', '')  # Establecer valor predeterminado
    fecha_fin = request.GET.get('fecha_fin', '')  # Establecer valor predeterminado

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
    if fecha_inicio:
        contenidos = contenidos.filter(fecha_publicacion__gte=fecha_inicio)

    # Si se proporciona fecha de fin pero no fecha de inicio, filtrar por el campo fecha_publicacion hasta la fecha de fin
    if fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__lte=fecha_fin)
    primeros_contenidos=contenidos.filter(estado='P')[:10]  
    # Renderizar la plantilla con los resultados y los valores de los filtros
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores,
            'q': q,  # Pasar el valor de búsqueda
            'categoria': categoria,  # Pasar el valor de categoría
            'autor': autor,  # Pasar el valor de autor
            'fecha_inicio': fecha_inicio,  # Pasar el valor de fecha de inicio
            'fecha_fin': fecha_fin  # Pasar el valor de fecha de fin
        }
    else:
        context={
            'autenticado': autenticado,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores,
            'q': q,  # Pasar el valor de búsqueda
            'categoria_filtro': categoria,  # Pasar el valor de categoría
            'autor': autor,  # Pasar el valor de autor
            'fecha_inicio': fecha_inicio,  # Pasar el valor de fecha de inicio
            'fecha_fin': fecha_fin  # Pasar el valor de fecha de fin
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
    # Obtén los roles del usuario
    roles_del_usuario = usuario_rol.roles.all()

    # Inicializa una lista para los permisos únicos
    permisos_del_usuario = []

    # Itera a través de los roles y agrega los permisos únicos a la lista
    for rol in roles_del_usuario:
        permisos_del_rol = rol.permisos.all()
        permisos_del_usuario.extend(permisos_del_rol)

    # Elimina los duplicados convirtiendo la lista a un conjunto y luego nuevamente a una lista
    permisos_del_usuario = list(set(permisos_del_usuario))

    return render(request, 'crear/main_trabajadores.html', {
    'usuario_rol': usuario_rol,
    'permisos_del_usuario': permisos_del_usuario,
    })



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
    model = Contenido
    template_name = 'articulo/articulo_detallado.html'
    
    def post(self, request, *args, **kwargs):
        # Procesar el formulario de comentarios aquí
        contenido = self.get_object()
        texto = request.POST.get('texto')
        autor = request.user  # El usuario actual
        if texto:
            Comentario.objects.create(contenido=contenido, autor=autor, texto=texto)

        # Recargar la página
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        contenido = self.get_object()
        contenido.veces_visto += 1
        contenido.save()
        comentarios = contenido.comentarios.all()
        context['comentarios'] = comentarios

        #Agrega contador de likes a la pagina
        likes = Likes.objects.get_or_create(contenido=contenido)[0]
        context['nro_likes'] = likes.user_likes_count()
        context['nro_dislikes'] = likes.user_dislikes_count()

        #Da una clase especial a los botones si el usuario ya dio like/dislike al contenido
        context['liked'] = 'notliked'
        context['disliked'] = 'notdisliked'
        if likes.user_likes.filter(username=self.request.user.username).exists():
            context['liked'] = 'liked'
        elif likes.user_dislikes.filter(username=self.request.user.username).exists():
            context['disliked'] = 'disliked'
        
        return context

class VistaArticulosEditor(DetailView):
    model = Contenido
    template_name='articulo/articulo_detallado_edicion.html'

class VistaArticulosRevision(DetailView):
    model = Contenido
    template_name='articulo/articulo_detallado_revision.html'



   
class VistaContenidos(ListView):
    model = Contenido
    template_name = 'Contenidos.html'
    context_object_name = 'contenidos'  # Nombre del objeto que se utilizará en la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c=self.object_list.filter(estado='P')
        paginator = Paginator(c, 4)  # Cambia '10' por la cantidad de elementos por página que desees
        page = self.request.GET.get('page')
        context['contenidos'] = paginator.get_page(page)
        context['categorias'] =Categoria.objects.filter(activo=True)
        context['autores'] = UsuarioRol.objects.filter(roles__nombre__contains='Autor') 
        context['promedio_calificaciones']=Contenido.objects.filter()
        # Calcula el promedio de calificaciones para todos los contenidos
        promedio_calificaciones = Contenido.objects.filter(estado='P').annotate(
            avg_calificacion=Avg('calificacion')
        )
        context['promedio_calificaciones'] = promedio_calificaciones.aggregate(Avg('avg_calificacion'))['avg_calificacion__avg']
        return context
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        categoria = self.request.GET.get('categoria', '')
        autor = self.request.GET.get('autor', '')
        fecha_inicio = self.request.GET.get('fecha_inicio', '')
        fecha_fin = self.request.GET.get('fecha_fin', '')

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
        if fecha_inicio:
            contenidos = contenidos.filter(fecha_publicacion__gte=fecha_inicio)

        # Si se proporciona fecha de fin pero no fecha de inicio, filtrar por el campo fecha_publicacion hasta la fecha de fin
        if fecha_fin:
            contenidos = contenidos.filter(fecha_publicacion__lte=fecha_fin)
        return contenidos
    

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
    # Define la cantidad de contenidos que deseas mostrar por página
    items_por_pagina = 2

    # Obtén los contenidos de las diferentes columnas
    contenidos_borrador = Contenido.objects.filter(estado='B')
    contenidos_en_edicion = Contenido.objects.filter(estado='E')
    contenidos_en_revision = Contenido.objects.filter(estado='R')
    contenidos_publicados = Contenido.objects.filter(estado='P')
    contenidos_inactivos = Contenido.objects.filter(estado='I')

    # Divide los contenidos en páginas
    paginador_borrador = Paginator(contenidos_borrador, items_por_pagina)
    paginador_edicion = Paginator(contenidos_en_edicion, items_por_pagina)
    paginador_revision = Paginator(contenidos_en_revision, items_por_pagina)
    paginador_publicados = Paginator(contenidos_publicados, items_por_pagina)
    paginador_inactivos = Paginator(contenidos_inactivos, items_por_pagina)

    # Obtén la página actual a partir del parámetro de la URL
    page_number = request.GET.get('page', 1)

    # Obtiene los contenidos de la página actual
    contenidos_borrador = paginador_borrador.get_page(page_number)
    contenidos_en_edicion = paginador_edicion.get_page(page_number)
    contenidos_en_revision = paginador_revision.get_page(page_number)
    contenidos_publicados = paginador_publicados.get_page(page_number)
    contenidos_inactivos = paginador_inactivos.get_page(page_number)

    # Otras consultas
    categorias = Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores = UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicadores = UsuarioRol.objects.filter(roles__nombre__contains='Publicador')

    context = {
        'categorias': categorias,
        'autores': autores,
        'editores': editores,
        'publicadores': publicadores,
        'contenidos_borrador': contenidos_borrador,
        'contenidos_en_edicion': contenidos_en_edicion,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_inactivos': contenidos_inactivos,
    }
    return render(request, 'vistas/vista_editor.html', context)


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
    # Define la cantidad de contenidos que deseas mostrar por página
    items_por_pagina = 2

    # Obtén los contenidos de las diferentes columnas
    contenidos_borrador = Contenido.objects.filter(estado='B', autor__username=request.user.username).order_by('-pk') #ordenar por id, de mayor a menor
    contenidos_en_edicion = Contenido.objects.filter(estado='E', autor__username=request.user.username).order_by('-pk')
    contenidos_en_revision = Contenido.objects.filter(estado='R', autor__username=request.user.username).order_by('-pk')
    contenidos_publicados = Contenido.objects.filter(estado='P', autor__username=request.user.username).order_by('-pk')
    contenidos_inactivos = Contenido.objects.filter(estado='I', autor__username=request.user.username).order_by('-pk')

    # Divide los contenidos en páginas
    paginador_borrador = Paginator(contenidos_borrador, items_por_pagina)
    paginador_edicion = Paginator(contenidos_en_edicion, items_por_pagina)
    paginador_revision = Paginator(contenidos_en_revision, items_por_pagina)
    paginador_publicados = Paginator(contenidos_publicados, items_por_pagina)
    paginador_inactivos = Paginator(contenidos_inactivos, items_por_pagina)

    # Obtén la página actual a partir del parámetro de la URL
    page_number = request.GET.get('page', 1)

    # Obtiene los contenidos de la página actual
    contenidos_borrador = paginador_borrador.get_page(page_number)
    contenidos_en_edicion = paginador_edicion.get_page(page_number)
    contenidos_en_revision = paginador_revision.get_page(page_number)
    contenidos_publicados = paginador_publicados.get_page(page_number)
    contenidos_inactivos = paginador_inactivos.get_page(page_number)

    # Otras consultas
    categorias = Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores = UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicadores = UsuarioRol.objects.filter(roles__nombre__contains='Publicador')

    context = {
        'categorias': categorias,
        'autores': autores,
        'editores': editores,
        'publicadores': publicadores,
        'contenidos_borrador': contenidos_borrador,
        'contenidos_en_edicion': contenidos_en_edicion,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_inactivos': contenidos_inactivos,
    }
    return render(request, 'vistas/vista_autor.html', context)

@login_required(login_url="/login")
def vista_mis_contenidos_borrador(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'vistas_autor/mis_contenidos_borrador.html',context)

  
@login_required(login_url="/login")
def vista_mis_contenidos_rechazados(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'vistas_autor/mis_contenidos_rechazados.html',context)

  

@login_required(login_url="/login")
def vista_mis_contenidos_publicados(request):
    contenidos=Contenido.objects.filter()
    context = {
        'contenidos': contenidos
    }
    return render(request,'vistas_autor/mis_contenidos_publicados.html',context)

    

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
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
        
    send_mail(subject="Contenido Publicado en la pagina", message=f"Su contenido {contenido.titulo} fue publicado en la pagina",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_publicador.html",
                                            {'nombre_publicador': request.user.username,
                                            'nombre_editor':contenido.ultimo_editor,
                                            'nombre_autor':contenido.autor_id,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
        
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
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    

    send_mail(subject="Contenido ha pasado al estado inactivo", message=f"Su contenido {contenido.titulo} fue bajado del sitio y se encuentra en estado inactivo",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_inactivar_publicador.html",
                                            {
                                            'nombre_editor':contenido.editor.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    

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
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    
    send_mail(subject="Has aceptado el rechazo de un contenido", message=f"Se acepto el rechazo de  {contenido.titulo}",
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
       # Define la cantidad de contenidos que deseas mostrar por página
    items_por_pagina = 2

    # Obtén los contenidos de las diferentes columnas
    contenidos_borrador = Contenido.objects.filter(estado='B')
    contenidos_en_edicion = Contenido.objects.filter(estado='E')
    contenidos_en_revision = Contenido.objects.filter(estado='R')
    contenidos_publicados = Contenido.objects.filter(estado='P')
    contenidos_inactivos = Contenido.objects.filter(estado='I')

    # Divide los contenidos en páginas
    paginador_borrador = Paginator(contenidos_borrador, items_por_pagina)
    paginador_edicion = Paginator(contenidos_en_edicion, items_por_pagina)
    paginador_revision = Paginator(contenidos_en_revision, items_por_pagina)
    paginador_publicados = Paginator(contenidos_publicados, items_por_pagina)
    paginador_inactivos = Paginator(contenidos_inactivos, items_por_pagina)

    # Obtén la página actual a partir del parámetro de la URL
    page_number = request.GET.get('page', 1)

    # Obtiene los contenidos de la página actual
    contenidos_borrador = paginador_borrador.get_page(page_number)
    contenidos_en_edicion = paginador_edicion.get_page(page_number)
    contenidos_en_revision = paginador_revision.get_page(page_number)
    contenidos_publicados = paginador_publicados.get_page(page_number)
    contenidos_inactivos = paginador_inactivos.get_page(page_number)

    # Otras consultas
    categorias = Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores = UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicadores = UsuarioRol.objects.filter(roles__nombre__contains='Publicador')

    context = {
        'categorias': categorias,
        'autores': autores,
        'editores': editores,
        'publicadores': publicadores, 
        'contenidos_borrador': contenidos_borrador,
        'contenidos_en_edicion': contenidos_en_edicion,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_inactivos': contenidos_inactivos,
    }
    return render(request, 'vistas/vista_publicador.html', context)

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
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    
    send_mail(subject="Se ha republicado  un contenido", message=f"Se reactivo  el contenido {contenido.titulo} de tu autoria, el publicador que realizo esta accion fue{contenido.publicador.username}",
                from_email=None,
                    recipient_list=[contenido.autor.email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)
    

    mensaje_edicion = render_to_string("email-notifs/email_notificacion_reactivar_contenido_publicador.html",
                                            {
                                            'nombre_publicador':contenido.publicador.username,
                                            'nombre_autor':contenido.autor.username,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    
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
    # Define la cantidad de contenidos que deseas mostrar por página
    items_por_pagina = 3

    # Consulta para obtener los contenidos
    contenido_borrador = Contenido.objects.filter(estado='B')
    contenidos_inactivos = Contenido.objects.filter(estado='I')
    contenidos_en_revision = Contenido.objects.filter(estado='R')
    contenidos_publicados = Contenido.objects.filter(estado='P')
    contenidos_en_edicion = Contenido.objects.filter(estado='E')

    # Divide los contenidos en páginas
    paginador_borrador = Paginator(contenido_borrador, items_por_pagina)
    paginador_inactivos = Paginator(contenidos_inactivos, items_por_pagina)
    paginador_revision = Paginator(contenidos_en_revision, items_por_pagina)
    paginador_publicados = Paginator(contenidos_publicados, items_por_pagina)
    paginador_edicion = Paginator(contenidos_en_edicion, items_por_pagina)

    # Obtén la página actual a partir del parámetro de la URL
    page_number = request.GET.get('page', 1)

    # Obtiene los contenidos de la página actual
    contenidos_borrador = paginador_borrador.get_page(page_number)
    contenidos_inactivos = paginador_inactivos.get_page(page_number)
    contenidos_en_revision = paginador_revision.get_page(page_number)
    contenidos_publicados = paginador_publicados.get_page(page_number)
    contenidos_en_edicion = paginador_edicion.get_page(page_number)

    # Otras consultas
    categorias = Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores = UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicadores = UsuarioRol.objects.filter(roles__nombre__contains='Publicador')

    context = {
        'categorias': categorias,
        'autores': autores,
        'editores': editores,
        'publicadores': publicadores,
        'contenidos_borrador': contenidos_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion': contenidos_en_edicion,
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
@login_required(login_url="/login")
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

    # Si se proporciona fecha de inicio pero no fecha de fin, filtrar por el campo fecha_publicacion desde la fecha de inicio
    if fecha_inicio and not fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__gte=fecha_inicio)

    # Si se proporciona fecha de fin pero no fecha de inicio, filtrar por el campo fecha_publicacion hasta la fecha de fin
    elif fecha_fin and not fecha_inicio:
        contenidos = contenidos.filter(fecha_publicacion__lte=fecha_fin)

    # Si se proporcionan fechas de inicio y fin, filtrar por el campo fecha_publicacion en el rango de esas fechas
    elif fecha_inicio and fecha_fin:
        contenidos = contenidos.filter(fecha_publicacion__range=[fecha_inicio, fecha_fin])
     # Define la cantidad de contenidos que deseas mostrar por página
    items_por_pagina = 2

    # Obtén los contenidos de las diferentes columnas
    contenidos_borrador = contenidos.filter(estado='B', autor__username=request.user.username)
    contenidos_en_edicion = contenidos.filter(estado='E', autor__username=request.user.username)
    contenidos_en_revision = contenidos.filter(estado='R', autor__username=request.user.username)
    contenidos_publicados = contenidos.filter(estado='P', autor__username=request.user.username)
    contenidos_inactivos = contenidos.filter(estado='I', autor__username=request.user.username)

    # Divide los contenidos en páginas
    paginador_borrador = Paginator(contenidos_borrador, items_por_pagina)
    paginador_edicion = Paginator(contenidos_en_edicion, items_por_pagina)
    paginador_revision = Paginator(contenidos_en_revision, items_por_pagina)
    paginador_publicados = Paginator(contenidos_publicados, items_por_pagina)
    paginador_inactivos = Paginator(contenidos_inactivos, items_por_pagina)

    # Obtén la página actual a partir del parámetro de la URL
    page_number = request.GET.get('page', 1)

    # Obtiene los contenidos de la página actual
    contenidos_borrador = paginador_borrador.get_page(page_number)
    contenidos_en_edicion = paginador_edicion.get_page(page_number)
    contenidos_en_revision = paginador_revision.get_page(page_number)
    contenidos_publicados = paginador_publicados.get_page(page_number)
    contenidos_inactivos = paginador_inactivos.get_page(page_number)

    # Otras consultas
    categorias = Categoria.objects.filter(activo=True)
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    editores = UsuarioRol.objects.filter(roles__nombre__contains='Editor')
    publicadores = UsuarioRol.objects.filter(roles__nombre__contains='Publicador')

    context = {
        'categorias':categorias,
        'autores':autores,
        'editores':editores,
        'publicadores':publicador,
        'contenidos_borrador': contenidos_borrador,
        'contenidos_inactivos': contenidos_inactivos,
        'contenidos_en_revision': contenidos_en_revision,
        'contenidos_publicados': contenidos_publicados,
        'contenidos_en_edicion':contenidos_en_edicion,
    }
    return render(request, 'vistas/vista_autor.html', context)
def historial_contenido(request, contenido_id):
    """
    Esta vista nos permite mantenernos al tanto de lso cambios que ha sufrido el contenido desde su creacion hasta su fin de ciclo. Detallando operaciones , personas responsables y fecha.
    Lo desplegamos en html historial_contenido.html pasandole como contexto el historial de el contenido y el contenido en si.
    """
    contenido = get_object_or_404(Contenido, id=contenido_id)  # Obtener la instancia de Contenido por su ID
    historial_prueba = HistorialContenido.objects.filter(contenido=contenido)
    context = {
        'historial_prueba': historial_prueba,
        'contenido': contenido  # Pasar la instancia de Contenido al contexto si es necesario
    }
    return render(request, 'historial_contenido.html', context)


def cambiar_version(request, contenido_id):
    """
    Muestra las versiones guardadas de un contenido empezando por las mas recientes. Muestra botones para restaurar las versiones.
    """
    contenido = get_object_or_404(Contenido, id=contenido_id)
    versiones = VersionesContenido.objects.filter(contenido_base=contenido).order_by('-fecha_version')
    vacio = not versiones.exists()
    
    context = {
        'contenido':contenido,
        'versiones': versiones,
        'vacio': vacio
    }
    return render(request, 'cambiar_version_contenido.html', context)

def guardar_version(contenido, numero_version):
    """
    Copia el contenido en un nuevo registro que se guarda con el numero de version proveido como argumento.
    """
    nueva_version = VersionesContenido(
        numero_version=numero_version,
        contenido_base= contenido,
        titulo=contenido.titulo,
        categoria=contenido.categoria,
        resumen=contenido.resumen,
        imagen=contenido.imagen,
        cuerpo=contenido.cuerpo,
        razon=contenido.razon,
    )

    nueva_version.save()

def aplicar_version(request, contenido_id, version_id):
    """
    Sobreescribe los campos de un contenido con los de una version previa. Agrega el cambio al historial del contenido.
    """
    contenido = get_object_or_404(Contenido, id=contenido_id)
    version = get_object_or_404(VersionesContenido, id=version_id)

    contenido.titulo= version.titulo
    contenido.categoria= version.categoria
    contenido.resumen= version.resumen
    contenido.imagen = version.imagen
    contenido.cuerpo= version.cuerpo
    contenido.razon = version.razon

    contenido.save()

    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El Autor con ID {contenido.autor.id},con username {contenido.autor.username},Aplico la version {version.numero_version} del contenido Con el Titulo {contenido.titulo}"
            )
    nuevo_cambio.save()
    return redirect('ContenidosBorrador')

@login_required
def dar_like(request, pk):
    """
    Guarda el like de un usuario a un contenido
    """
    usuario = UsuarioRol.objects.get(username=request.user.username)
    # Buscar si el usuario ya dio like o dislike
    likes = Likes.objects.filter(contenido__id=pk, user_likes=usuario)
    dislikes = Likes.objects.filter(contenido__id=pk, user_dislikes=usuario)

    # Si existe el like, quitarlo y salir (el usuario quito su like)
    if(likes.exists()):
        likes[0].user_likes.remove(usuario)
        return redirect('detalles_articulo', pk=pk)
    # Si existe el dislike quitalo, agregar el usuario a los likes y salir
    elif(dislikes.exists()):
        dislikes[0].user_dislikes.remove(usuario)
    
    # Agregar usuario a los likes del contenido y salir
    Likes.objects.get(contenido__id=pk).user_likes.add(usuario)
    return redirect('detalles_articulo', pk=pk)

@login_required
def dar_dislike(request, pk):
    """
    Guarda el dislike de un usuario a un contenido
    """
    usuario = UsuarioRol.objects.get(username=request.user.username)
    # Buscar si el usuario ya dio like o dislike
    likes = Likes.objects.filter(contenido__id=pk, user_likes=usuario)
    dislikes = Likes.objects.filter(contenido__id=pk, user_dislikes=usuario)
    
    # Si existe el dislike quitalo y salir (el usuario quito su dislike)
    if(dislikes.exists()):
        dislikes[0].user_dislikes.remove(usuario)
        return redirect('detalles_articulo', pk=pk)

    # Si existe el like, quitarlo y continuar
    elif(likes.exists()):
        likes[0].user_likes.remove(usuario)

    # Agregar usuario a los dislikes del contenido y salir
    Likes.objects.get(contenido__id=pk).user_dislikes.add(usuario)
    return redirect('detalles_articulo', pk=pk)
def calificar_contenido(request, contenido_id):
    contenido = get_object_or_404(Contenido, id=contenido_id)
    usuario = request.user
    calificacion = Decimal(request.POST.get('calificacion',0))

    # Verificar si el usuario ya ha calificado el contenido
    calificacion_existente, created = Calificacion.objects.get_or_create(contenido=contenido, usuario=usuario, defaults={'calificacion': calificacion})

    if not created:
        # Actualizar la calificación existente
        calificacion_existente.calificacion = calificacion
        calificacion_existente.save()

    # Recalcular la calificación media del contenido
    calificaciones = Calificacion.objects.filter(contenido=contenido)
    promedio_calificaciones = calificaciones.aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    contenido.promedio_calificaciones = promedio_calificaciones
    contenido.save()

    # Llama a la función para actualizar la calificación de estrellas
    actualizar_calificacion_estrellas(contenido)

    return redirect('detalles_articulo', pk=contenido.id)

def actualizar_calificacion_estrellas(contenido):
    """Actualiza la calificación de estrellas de un contenido."""

    promedio_calificaciones = contenido.promedio_calificaciones
    num_estrellas = round(promedio_calificaciones)  # Redondeamos al número entero más cercano

    # Establecer la clase de cada estrella en función del número de estrellas
    for i in range(1, 6):
        estrella_active = i <= num_estrellas

        # Guardar el estado de la estrella en tu modelo Contenido
        setattr(contenido, f'stars_{i}', estrella_active)

    contenido.save()

def aumentar_veces_compartido(request, contenido_id):
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.veces_compartido += 1
    contenido.save()
    return redirect('detalles_articulo', pk=contenido.id)


  
def qr_code(request, pk):
    contenido = get_object_or_404(Contenido, id=pk)
    aumentar_veces_compartido(request,pk)
    url = request.build_absolute_uri(f'/articulo/{pk}')
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response