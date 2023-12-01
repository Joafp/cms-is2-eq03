from pyexpat.errors import messages
from django.forms.models import BaseModelForm
from django.urls import reverse
from html.parser import HTMLParser
from typing import Any
from django.http import HttpResponseRedirect
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
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from decimal import Decimal
from django.db.models import Sum
from .models import Categoria,Favorito,Reporte
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
import plotly.express as px
from datetime import datetime
from GestionCuentas.models import Rol
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

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
            self.object.titulo_abreviado=self.object.titulo[:20]
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
        if "enviar_editor" in self.request.POST or "publicar_ahora" in self.request.POST:
            # Publica directamente si la categoria es no moderada
            if self.object.categoria.moderada == False:
                fecha = self.request.POST.get("fecha_programada")
                hora = self.request.POST.get('hora_programada')
                programado = True
                if len(fecha) == 0 or "publicar_ahora" in self.request.POST:
                    programado = False
                    fecha = datetime.now()
                else:
                    fecha = datetime.strptime(fecha+' '+hora, '%Y-%m-%d %H:%M')
                self.object.ultimo_publicador=self.request.user.username
                self.object.estado = 'P'
                self.object.fecha_publicacion = fecha
                self.object.save()
                if programado:
                    nuevo_cambio = HistorialContenido(
                        contenido=self.object,  # Asigna la instancia de Contenido, no el ID
                        cambio=f"Se programo el contenido el con el Titulo {self.object.titulo} por el autor {self.object.autor.username}, para ser publicado en fecha {fecha}"
                    )
                    nuevo_cambio.save()

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
            
            return redirect('vista_autor')
            
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  
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
    contenidos=Contenido.objects.filter(autor__in=autores_activos, estado='P', fecha_publicacion__lte=timezone.datetime.now()).order_by('-fecha_publicacion') # Ocultar contenido no publicado
    autores = UsuarioRol.objects.filter(roles__nombre__contains='Autor')
    primeros_contenidos = contenidos.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now())
    page = request.GET.get('page', 1)
    paginator = Paginator(contenidos, 10)  # Show 10 contents per page
    try:
        primeros_contenidos = paginator.page(page)
    except PageNotAnInteger:
        primeros_contenidos = paginator.page(1)
    except EmptyPage:
        primeros_contenidos = paginator.page(paginator.num_pages)
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        favoritos = Favorito.objects.filter(user_sub=usuario_rol)
        user_favoritos = [favorito.categoria.pk for favorito in favoritos]
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores,
            'user_favoritos': user_favoritos
        }
    else:
        context={
            'autenticado': autenticado,
            'categorias': categorias,
            'contenido':primeros_contenidos,
            'autores':autores,
            'user_favoritos': []
        }    
    print("Usuario: ",autenticado)
      # Paginación
    return render(request, 'crear/main.html',context )
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
    primeros_contenidos = contenidos.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now())[:10]
      # Obtiene los parámetros de búsqueda del formulario
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')  # Establecer valor predeterminado
    autor = request.GET.get('autor', '')  # Establecer valor predeterminado
    fecha_inicio = request.GET.get('fecha_inicio', '')  # Establecer valor predeterminado
    fecha_fin = request.GET.get('fecha_fin', '')  # Establecer valor predeterminado

    # Inicializar el queryset con todos los contenidos
    contenidos = Contenido.objects.all()

    #Filtrar contenidos no publicados
    contenidos = contenidos.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now())

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
    primeros_contenidos=contenidos.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now())[:10]  
    # Renderizar la plantilla con los resultados y los valores de los filtros
    page = request.GET.get('page', 1)
    paginator = Paginator(contenidos, 10)  # Show 10 contents per page
    try:
        primeros_contenidos = paginator.page(page)
    except PageNotAnInteger:
        primeros_contenidos = paginator.page(1)
    except EmptyPage:
        primeros_contenidos = paginator.page(paginator.num_pages)
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        favoritos = Favorito.objects.filter(user_sub=usuario_rol)
        user_favoritos = [favorito.categoria.pk for favorito in favoritos]
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
            'fecha_fin': fecha_fin , # Pasar el valor de fecha de fin
            'user_favoritos': []
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
            'fecha_fin': fecha_fin , # Pasar el valor de fecha de fin
            'user_favoritos': []
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
        permisos_del_usuario = []
        usuario_rol = UsuarioRol.objects.get(username=self.request.user.username)
        roles_del_usuario = usuario_rol.roles.all()
        # Itera a través de los roles y agrega los permisos únicos a la lista
        for rol in roles_del_usuario:
            permisos_del_rol = rol.permisos.all()
            permisos_del_usuario.extend(permisos_del_rol)
        context['permisos_del_usuario']=permisos_del_usuario    
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
        c=self.object_list.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now()) # Oculta los contenidos programados para publicarse en fechas futuras
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

        #Filtrar contenidos no publicados
        contenidos = contenidos.filter(estado='P', fecha_publicacion__lte=timezone.datetime.now())

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
    contenidos=Contenido.objects.filter(categoria_id=categoria.id, estado='P', fecha_publicacion__lte=datetime.now()) # Oculta contenidos no publicados
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
        if 'usuario' in request.GET:vista_editor
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
    if request.method == 'POST':
        # Obtén el objeto de contenido basado en algún criterio, como un ID
        contenido = Contenido.objects.get(id=contenido_id)
        destacado = request.POST.get('destacado')
        if destacado == '1':
            contenido.destacado = 1
        else:
            contenido.destacado = 0
        contenido.estado = 'P'
        contenido.publicador= UsuarioRol.objects.get(username=request.user.username)
        contenido.ultimo_publicador=request.user.username
        contenido.fecha_publicacion = timezone.now()

        if "programar_publicacion" in request.POST:
            fecha = request.POST.get('fecha_programada')
            hora = request.POST.get('hora_programada')
            contenido.fecha_publicacion = datetime.strptime(fecha+' '+hora, '%Y-%m-%d %H:%M')
            #contenido.fecha_publicacion = datetime.strptime(fecha, '%Y-%m-%d')
            contenido.save()
            nuevo_cambio = HistorialContenido(
                    contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                    cambio=f"Se programo la publicacion del contenido con el Titulo {contenido.titulo} por el autor {contenido.autor.username} Para la fecha {contenido.fecha_publicacion}. El contenido pasa a estado 'Publicado'. El Publicador que acepto la publicacion fue : {contenido.ultimo_publicador}"
            )
            nuevo_cambio.save()
            send_mail(subject="Contenido Progamado para publicarse en la pagina", message=f"Su contenido {contenido.titulo} fue programado para publicarse en la pagina en la fecha {contenido.fecha_publicacion}",
                    from_email=None,
                        recipient_list=[UsuarioRol.objects.get(username=contenido.publicador.username).email, 'is2cmseq03@gmail.com', ],
                        html_message=None)
            return redirect('vista_pub')
        contenido.titulo_abreviado=contenido.titulo[:20]
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
        
        ###mensaje a los usuarios
        categoria_contenido = contenido.categoria

        # Obtener los favoritos asociados a la categoría del contenido actual
        categorias_favoritas = Favorito.objects.filter(categoria=categoria_contenido)
        for favorito in categorias_favoritas:
            # Recuperar usuarios asociados a la categoría favorita
            usuarios_favoritos = favorito.user_sub.all()
            for usuario in usuarios_favoritos:
                # Obtener la información relevante para el correo electrónico
                categoria_nombre = favorito.categoria.nombre
                email_usuario = usuario.email

                # Aquí puedes personalizar el mensaje del correo electrónico
                mensaje = f"Hola {usuario.username}, la categoría '{categoria_nombre}' que has marcado como favorita tiene una actualización. ¡Échale un vistazo!"

                # Envío del correo electrónico
                send_mail(
                    subject="Actualización en tu categoría favorita",
                    message=mensaje,
                    from_email=None,  # Puedes configurar el correo del remitente si es necesario
                    recipient_list=[email_usuario],  # Envía el correo al usuario asociado a la categoría
                    html_message=None,  # Mensaje HTML opcional
                )
        # Redirige al usuario a la vista del editor
        return redirect('vista_pub')

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
    return redirect('vista_autor')
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
    """
    Comentado el 02/11/2023
    Esta vista sirve para calificar un contneido, luego de calificar hacemos un promedio de calificaiones y mostramos.

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
    """
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
    """
    Documentado el 2/11/2023
    La vista sirve para actualizar una calificaion, es decir cuando un usuario ya califico un contenido y desea cambiar la calificacion
    
    def actualizar_calificacion_estrellas(contenido):
        promedio_calificaciones = contenido.promedio_calificaciones
        num_estrellas = round(promedio_calificaciones)  # Redondeamos al número entero más cercano

        # Establecer la clase de cada estrella en función del número de estrellas
        for i in range(1, 6):
            estrella_active = i <= num_estrellas

            # Guardar el estado de la estrella en tu modelo Contenido
            setattr(contenido, f'stars_{i}', estrella_active)

        contenido.save()
  
    """

    promedio_calificaciones = contenido.promedio_calificaciones
    num_estrellas = round(promedio_calificaciones)  # Redondeamos al número entero más cercano

    # Establecer la clase de cada estrella en función del número de estrellas
    for i in range(1, 6):
        estrella_active = i <= num_estrellas

        # Guardar el estado de la estrella en tu modelo Contenido
        setattr(contenido, f'stars_{i}', estrella_active)

    contenido.save()

def aumentar_veces_compartido(request, contenido_id):
    """
    Documentado el 02/11/2023
    Esta view se encarga de aumentar el contador de veces compartido de un contenido

    def aumentar_veces_compartido(request, contenido_id):
        contenido = Contenido.objects.get(id=contenido_id)
        contenido.veces_compartido += 1
        contenido.save()
        return redirect('detalles_articulo', pk=contenido.id)

    """
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.veces_compartido += 1
    contenido.save()
    return redirect('detalles_articulo', pk=contenido.id)


  
def qr_code(request, pk):
    """
    Documentado 02/11/2023
    Esta vista sirve para generar el codigo qr y que muestre el link de la pagina actual
    def qr_code(request, pk):
        contenido = get_object_or_404(Contenido, id=pk)
        aumentar_veces_compartido(request,pk)
        url = request.build_absolute_uri(f'/articulo/{pk}')
        img = qrcode.make(url)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response
    """
    contenido = get_object_or_404(Contenido, id=pk)
    """aumentar_veces_compartido(request,pk)"""
    url = request.build_absolute_uri(f'/articulo/{pk}')
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

def toggle_destacado(request, pk):
    """
    Comentado 29-11-23
    Esta funcion se creo para pdoear destacar un contenido , el valro 1 significa destacado y el valor 0 no destacado 
    def toggle_destacado(request, pk):
        # Obtener el contenido
        contenido = get_object_or_404(Contenido, pk=pk)
        # Cambiar el estado de destacado del contenido
        contenido.destacado = not contenido.destacado
        contenido.save()

        # Redirigir a la página de detalles del contenido
        return HttpResponseRedirect(reverse('detalles_articulo', kwargs={'pk': pk}))
    """
    # Obtener el contenido
    contenido = get_object_or_404(Contenido, pk=pk)
    # Cambiar el estado de destacado del contenido
    contenido.destacado = not contenido.destacado
    contenido.save()

    # Redirigir a la página de detalles del contenido
    return HttpResponseRedirect(reverse('detalles_articulo', kwargs={'pk': pk}))

@login_required
def dar_favorito(request, pk):
    """
    Comentado 29-11-23
    Esta funcion se creo con el fin de que un usuario pueda marcar como favorita una categoria
    def dar_favorito(request, pk):
        usuario = UsuarioRol.objects.get(username=request.user.username)
        
        # Verificar si ya existe un objeto Favorito para esta categoría
        try:
            favorito_existente = Favorito.objects.get(categoria__id=pk)
        except Favorito.DoesNotExist:
            # Si no existe, crea un nuevo objeto Favorito para esta categoría
            nueva_categoria_favorita = Favorito.objects.create(categoria_id=pk)
            nueva_categoria_favorita.save()

        # Una vez que se tiene un objeto Favorito para la categoría, agrega el usuario como favorito
        favorito = Favorito.objects.get(categoria__id=pk)
        favorito.user_sub.add(usuario)
        
        return redirect('MenuPrincipal')
    """
    usuario = UsuarioRol.objects.get(username=request.user.username)
    
    # Verificar si ya existe un objeto Favorito para esta categoría
    try:
        favorito_existente = Favorito.objects.get(categoria__id=pk)
    except Favorito.DoesNotExist:
        # Si no existe, crea un nuevo objeto Favorito para esta categoría
        nueva_categoria_favorita = Favorito.objects.create(categoria_id=pk)
        nueva_categoria_favorita.save()

    # Una vez que se tiene un objeto Favorito para la categoría, agrega el usuario como favorito
    favorito = Favorito.objects.get(categoria__id=pk)
    favorito.user_sub.add(usuario)
    
    return redirect('MenuPrincipal')

@login_required
def quitar_favorito(request, pk):
    """
    Comentado 29-11-23
    Esta funcion se creo con el fin de quitar de la lista de categorias favoritas de un usuario, esto mediante el boton en el menu principal
    def quitar_favorito(request, pk):
    
        usuario = UsuarioRol.objects.get(username=request.user.username)
        
        # Verificar si ya existe un objeto Favorito para esta categoría
        try:
            favorito_existente = Favorito.objects.get(categoria__id=pk)
        except Favorito.DoesNotExist:
            # Si no existe, crea un nuevo objeto Favorito para esta categoría
            nueva_categoria_favorita = Favorito.objects.create(categoria_id=pk)
            nueva_categoria_favorita.save()

        # Una vez que se tiene un objeto Favorito para la categoría, agrega el usuario como favorito
        favorito = Favorito.objects.get(categoria__id=pk)
        favorito.user_sub.remove(usuario)
        
        return redirect('MenuPrincipal')
    """
    usuario = UsuarioRol.objects.get(username=request.user.username)
    
    # Verificar si ya existe un objeto Favorito para esta categoría
    try:
        favorito_existente = Favorito.objects.get(categoria__id=pk)
    except Favorito.DoesNotExist:
        # Si no existe, crea un nuevo objeto Favorito para esta categoría
        nueva_categoria_favorita = Favorito.objects.create(categoria_id=pk)
        nueva_categoria_favorita.save()

    # Una vez que se tiene un objeto Favorito para la categoría, agrega el usuario como favorito
    favorito = Favorito.objects.get(categoria__id=pk)
    favorito.user_sub.remove(usuario)
    
    return redirect('MenuPrincipal')
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)
from django.db.models import Count, Sum
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from django.utils.html import strip_tags
def grafico_estadisticas(request):
    """
    Comentado 29-11-2023
    Esta funcion nos permite crear graficas con contenidos en estado publicado , para luego mostrar a publicadores. Esta vista trae likes , dislikes , veces compartidos , categorias
    mas vistas , etc.

    def grafico_estadisticas(request):
    # Obtener las categorías y la cantidad de vistas de cada una
    categorias = Categoria.objects.all()
    datos_categorias = []
    for categoria in categorias:
        cantidad_vistas = Contenido.objects.filter(categoria=categoria).aggregate(total=Sum('veces_visto'))['total'] or 0
        datos_categorias.append({'Categoria': categoria.nombre, 'Vistas': cantidad_vistas})

    # Crear el gráfico de barras para las categorías más vistas
    fig_categorias = px.bar(datos_categorias, x='Categoria', y='Vistas', title='Categorías más vistas')
    plot_categorias = fig_categorias.to_html(full_html=False, default_height=500, default_width=700)
   # Obtener los contenidos con más likes y sus categorías
    contenidos_likes = Likes.objects.values('contenido__titulo_abreviado', 'contenido__categoria__nombre').annotate(total_likes=Count('user_likes')).order_by('-total_likes')
    titulos = [strip_tags(contenido_like['contenido__titulo_abreviado']) for contenido_like in contenidos_likes]
    total_likes = [contenido_like['total_likes'] for contenido_like in contenidos_likes]

    data = [go.Bar(x=titulos, y=total_likes)]
    layout = go.Layout(title='Contenidos con más Likes', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Likes'))
    fig = go.Figure(data=data, layout=layout)
    plot_contenidos_likes = plot(fig, output_type='div', include_plotlyjs=False)
   #dislikes
    contenidos_dislikes = Likes.objects.values('contenido__titulo_abreviado', 'contenido__categoria__nombre').annotate(total_dislikes=Count('user_dislikes')).order_by('-total_dislikes')
    titulos = [strip_tags(contenido_dislike['contenido__titulo_abreviado']) for contenido_dislike in contenidos_dislikes]
    total_dislikes = [contenido_dislike['total_dislikes'] for contenido_dislike in contenidos_dislikes]

    data = [go.Bar(x=titulos, y=total_dislikes)]
    layout = go.Layout(title='Contenidos con más Dislikes', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Dislikes'))
    fig = go.Figure(data=data, layout=layout)
    plot_contenidos_dislikes = plot(fig, output_type='div', include_plotlyjs=False)
    #mas vistos
    contenidos_mas_vistos = Contenido.objects.filter(estado='P').order_by('-veces_visto')
    titulos = [strip_tags(contenido.titulo_abreviado) for contenido in contenidos_mas_vistos]
    veces_vistos = [contenido.veces_visto for contenido in contenidos_mas_vistos]
    data = [go.Bar(x=titulos, y=veces_vistos)]
    layout = go.Layout(title='Contenidos más vistos')
    fig = go.Figure(data=data, layout=layout)
    plot_contenido_vistas = plot(fig, output_type='div', include_plotlyjs=False)
    #compartidos
    contenidos_compartidos = Contenido.objects.filter(estado='P').order_by('-veces_compartido')
    titulos = [strip_tags(contenido.titulo_abreviado) for contenido in contenidos_compartidos]
    veces_compartidos = [contenido.veces_compartido for contenido in contenidos_compartidos]
    data = [go.Bar(x=titulos, y=veces_compartidos)]
    layout = go.Layout(title='Contenidos más Compartidos')
    fig = go.Figure(data=data, layout=layout)
    plot_veces_compartidos = plot(fig, output_type='div', include_plotlyjs=False)

    #Calificacion
    contenidos_calificados = Contenido.objects.filter(estado='P').order_by('-promedio_calificaciones')
    titulos = [strip_tags(contenido.titulo_abreviado) for contenido in contenidos_calificados]
    promedio = [contenido.promedio_calificaciones for contenido in contenidos_calificados]
    data = [go.Bar(x=titulos, y=promedio)]
    layout = go.Layout(title='Contenidos mejores calificados')
    fig = go.Figure(data=data, layout=layout)
    plot_calificacion = plot(fig, output_type='div', include_plotlyjs=False)
    context = {
        'plot_html': plot_categorias,
        'plot_contenidos_likes': plot_contenidos_likes,
        'plot_contenidos_dislikes': plot_contenidos_dislikes,
        'plot_contenido_vistas': plot_contenido_vistas,
        'plot_veces_compartidos': plot_veces_compartidos,
        'plot_calificacion':plot_calificacion
    }
    return render(request, 'graficos/graficos.html', context)
    """
    # Obtener las categorías y la cantidad de vistas de cada una
    categorias = Categoria.objects.all()
    datos_categorias = []
    for categoria in categorias:
        cantidad_vistas = Contenido.objects.filter(categoria=categoria).aggregate(total=Sum('veces_visto'))['total'] or 0
        datos_categorias.append({'Categoria': categoria.nombre, 'Vistas': cantidad_vistas})

    # Crear el gráfico de barras para las categorías más vistas
    fig_categorias = px.bar(datos_categorias, x='Categoria', y='Vistas', title='Categorías más vistas')
    plot_categorias = fig_categorias.to_html(full_html=False, default_height=500, default_width=700)
   # Obtener los contenidos con más likes y sus categorías
    contenidos_likes = Likes.objects.values('contenido__id', 'contenido__categoria__nombre').annotate(total_likes=Count('user_likes')).order_by('-total_likes')
    titulos = [strip_tags(contenido_like['contenido__id']) for contenido_like in contenidos_likes]
    total_likes = [contenido_like['total_likes'] for contenido_like in contenidos_likes]

    data = [go.Bar(x=titulos, y=total_likes)]
    layout = go.Layout(title='Contenidos con más Likes', xaxis=dict(title='ID'), yaxis=dict(title='Total Likes'))
    fig = go.Figure(data=data, layout=layout)
    plot_contenidos_likes = plot(fig, output_type='div', include_plotlyjs=False)
   #dislikes
    contenidos_dislikes = Likes.objects.values('contenido__id', 'contenido__id').annotate(total_dislikes=Count('user_dislikes')).order_by('-total_dislikes')
    titulos = [strip_tags(contenido_dislike['contenido__id']) for contenido_dislike in contenidos_dislikes]
    total_dislikes = [contenido_dislike['total_dislikes'] for contenido_dislike in contenidos_dislikes]

    data = [go.Bar(x=titulos, y=total_dislikes)]
    layout = go.Layout(title='Contenidos con más Dislikes', xaxis=dict(title='ID'), yaxis=dict(title='Total Dislikes'))
    fig = go.Figure(data=data, layout=layout)
    plot_contenidos_dislikes = plot(fig, output_type='div', include_plotlyjs=False)
   #mas vistos
    contenidos_mas_vistos = Contenido.objects.filter(estado='P').order_by('-veces_visto')
    titulos = [strip_tags(contenido.id) for contenido in contenidos_mas_vistos]
    veces_vistos = [contenido.veces_visto for contenido in contenidos_mas_vistos]
    data = [go.Bar(x=titulos, y=veces_vistos)]
    layout = go.Layout(title='Contenidos más vistos')
    fig = go.Figure(data=data, layout=layout)
    plot_contenido_vistas = plot(fig, output_type='div', include_plotlyjs=False)
    #compartidos
    contenidos_compartidos = Contenido.objects.filter(estado='P').order_by('-veces_compartido')
    titulos = [strip_tags(contenido.id) for contenido in contenidos_compartidos]
    veces_compartidos = [contenido.veces_compartido for contenido in contenidos_compartidos]
    data = [go.Bar(x=titulos, y=veces_compartidos)]
    layout = go.Layout(title='Contenidos más Compartidos')
    fig = go.Figure(data=data, layout=layout)
    plot_veces_compartidos = plot(fig, output_type='div', include_plotlyjs=False)

    #Calificacion
    contenidos_calificados = Contenido.objects.filter(estado='P').order_by('-promedio_calificaciones')
    titulos = [strip_tags(contenido.id) for contenido in contenidos_calificados]
    promedio = [contenido.promedio_calificaciones for contenido in contenidos_calificados]
    data = [go.Bar(x=titulos, y=promedio)]
    layout = go.Layout(title='Contenidos mejores calificados')
    fig = go.Figure(data=data, layout=layout)
    plot_calificacion = plot(fig, output_type='div', include_plotlyjs=False)
    context = {
        'plot_html': plot_categorias,
        'plot_contenidos_likes': plot_contenidos_likes,
        'plot_contenidos_dislikes': plot_contenidos_dislikes,
        'plot_contenido_vistas': plot_contenido_vistas,
        'plot_veces_compartidos': plot_veces_compartidos,
        'plot_calificacion':plot_calificacion
    }
    return render(request, 'graficos/graficos.html', context)
from collections import Counter
from collections import defaultdict
def estadistica_autor(request):
    """
    Comentado 29-11-23
    
    Esta funcion nos permite juntar informacion sobre los contenidos en estado publicado , que ppertenezca al autor. Estos datos 
    Nos permite para pdoer reflejar en graficos y crear una vista para mostrar al autor las estadisticas de sus publicaciones en estado Publicado
    def estadistica_autor(request):
    usuario_actual = request.user
    nombre_usuario = usuario_actual.username if usuario_actual else None

    # Obtener contenidos del usuario actual que estén publicados ('P')
    contenidos_usuario_actual = Contenido.objects.filter(autor__username=nombre_usuario, estado='P')

    # Inicializar contadores para likes, dislikes, vistas y compartidos
    likes_contenidos = Counter()
    dislikes_contenidos = Counter()
    vistas_contenidos = Counter()
    compartidos_contenidos = Counter()
    calificaciones_contenidos = defaultdict(int)
    for contenido in contenidos_usuario_actual:
        # Obtener los likes, dislikes, vistas y compartidos para cada contenido del usuario actual
        likes_contenido = Likes.objects.filter(contenido=contenido, user_likes__isnull=False).count()
        dislikes_contenido = Likes.objects.filter(contenido=contenido, user_dislikes__isnull=False).count()
        vistas_contenido = contenido.veces_visto
        compartidos_contenido = contenido.veces_compartido
        calificacion_contenido = contenido.promedio_calificaciones
        # Agregar los valores a los contadores por título de contenido
        likes_contenidos[strip_tags(contenido.titulo_abreviado)] = likes_contenido
        dislikes_contenidos[strip_tags(contenido.titulo_abreviado)] = dislikes_contenido
        vistas_contenidos[strip_tags(contenido.titulo_abreviado)] = vistas_contenido
        compartidos_contenidos[strip_tags(contenido.titulo_abreviado)] = compartidos_contenido
        calificaciones_contenidos[strip_tags(contenido.titulo_abreviado)] = calificacion_contenido
    # Ordenar los contenidos por likes, dislikes, vistas y compartidos de mayor a menor
    likes_ordenados = dict(sorted(likes_contenidos.items(), key=lambda item: item[1], reverse=True))
    dislikes_ordenados = dict(sorted(dislikes_contenidos.items(), key=lambda item: item[1], reverse=True))
    vistas_ordenadas = dict(sorted(vistas_contenidos.items(), key=lambda item: item[1], reverse=True))
    compartidos_ordenados = dict(sorted(compartidos_contenidos.items(), key=lambda item: item[1], reverse=True))
    calificaciones_ordenadas = dict(sorted(calificaciones_contenidos.items(), key=lambda item: item[1], reverse=True))

    # Crear los gráficos de barras con los datos ordenados
    data_likes = [go.Bar(x=list(likes_ordenados.keys()), y=list(likes_ordenados.values()))]
    layout_likes = go.Layout(title='Contenidos con más Likes', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Likes'))
    fig_likes = go.Figure(data=data_likes, layout=layout_likes)
    plot_contenidos_likes = plot(fig_likes, output_type='div', include_plotlyjs=False)

    data_dislikes = [go.Bar(x=list(dislikes_ordenados.keys()), y=list(dislikes_ordenados.values()))]
    layout_dislikes = go.Layout(title='Contenidos con más Dislikes', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Dislikes'))
    fig_dislikes = go.Figure(data=data_dislikes, layout=layout_dislikes)
    plot_contenidos_dislikes = plot(fig_dislikes, output_type='div', include_plotlyjs=False)

    data_vistas = [go.Bar(x=list(vistas_ordenadas.keys()), y=list(vistas_ordenadas.values()))]
    layout_vistas = go.Layout(title='Contenidos más Vistos', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Vistas'))
    fig_vistas = go.Figure(data=data_vistas, layout=layout_vistas)
    plot_contenidos_vistas = plot(fig_vistas, output_type='div', include_plotlyjs=False)

    data_compartidos = [go.Bar(x=list(compartidos_ordenados.keys()), y=list(compartidos_ordenados.values()))]
    layout_compartidos = go.Layout(title='Contenidos más Compartidos', xaxis=dict(title='Títulos'), yaxis=dict(title='Total Compartidos'))
    fig_compartidos = go.Figure(data=data_compartidos, layout=layout_compartidos)
    plot_contenidos_compartidos = plot(fig_compartidos, output_type='div', include_plotlyjs=False)
    
    data_calificaciones = [go.Bar(x=list(calificaciones_ordenadas.keys()), y=list(calificaciones_ordenadas.values()))]
    layout_calificaciones = go.Layout(title='Contenidos mejor Calificados', xaxis=dict(title='Títulos'), yaxis=dict(title='Calificación'))
    fig_calificaciones = go.Figure(data=data_calificaciones, layout=layout_calificaciones)
    plot_contenidos_calificados = plot(fig_calificaciones, output_type='div', include_plotlyjs=False)


    context = {
        'plot_contenidos_likes': plot_contenidos_likes,
        'plot_contenidos_dislikes': plot_contenidos_dislikes,
        'plot_contenidos_vistas': plot_contenidos_vistas,
        'plot_contenidos_compartidos': plot_contenidos_compartidos,
        'plot_contenidos_calificados': plot_contenidos_calificados
    }
    return render(request, 'graficos/graficos_autor.html', context)
    """
    usuario_actual = request.user
    nombre_usuario = usuario_actual.username if usuario_actual else None

    # Obtener contenidos del usuario actual que estén publicados ('P')
    contenidos_usuario_actual = Contenido.objects.filter(autor__username=nombre_usuario, estado='P')

    # Inicializar contadores para likes, dislikes, vistas y compartidos
    likes_contenidos = Counter()
    dislikes_contenidos = Counter()
    vistas_contenidos = Counter()
    compartidos_contenidos = Counter()
    calificaciones_contenidos = defaultdict(int)
    for contenido in contenidos_usuario_actual:
        # Obtener los likes, dislikes, vistas y compartidos para cada contenido del usuario actual
        likes_contenido = Likes.objects.filter(contenido=contenido, user_likes__isnull=False).count()
        dislikes_contenido = Likes.objects.filter(contenido=contenido, user_dislikes__isnull=False).count()
        vistas_contenido = contenido.veces_visto
        compartidos_contenido = contenido.veces_compartido
        calificacion_contenido = contenido.promedio_calificaciones
        # Agregar los valores a los contadores por título de contenido
        likes_contenidos[strip_tags(contenido.id)] = likes_contenido
        dislikes_contenidos[strip_tags(contenido.id)] = dislikes_contenido
        vistas_contenidos[strip_tags(contenido.id)] = vistas_contenido
        compartidos_contenidos[strip_tags(contenido.id)] = compartidos_contenido
        calificaciones_contenidos[strip_tags(contenido.id)] = calificacion_contenido
    # Ordenar los contenidos por likes, dislikes, vistas y compartidos de mayor a menor
    likes_ordenados = dict(sorted(likes_contenidos.items(), key=lambda item: item[1], reverse=True))
    dislikes_ordenados = dict(sorted(dislikes_contenidos.items(), key=lambda item: item[1], reverse=True))
    vistas_ordenadas = dict(sorted(vistas_contenidos.items(), key=lambda item: item[1], reverse=True))
    compartidos_ordenados = dict(sorted(compartidos_contenidos.items(), key=lambda item: item[1], reverse=True))
    calificaciones_ordenadas = dict(sorted(calificaciones_contenidos.items(), key=lambda item: item[1], reverse=True))

    # Crear los gráficos de barras con los datos ordenados
    data_likes = [go.Bar(x=list(likes_ordenados.keys()), y=list(likes_ordenados.values()))]
    layout_likes = go.Layout(title='Contenidos con más Likes', xaxis=dict(title='ID'), yaxis=dict(title='Total Likes'))
    fig_likes = go.Figure(data=data_likes, layout=layout_likes)
    plot_contenidos_likes = plot(fig_likes, output_type='div', include_plotlyjs=False)

    data_dislikes = [go.Bar(x=list(dislikes_ordenados.keys()), y=list(dislikes_ordenados.values()))]
    layout_dislikes = go.Layout(title='Contenidos con más Dislikes', xaxis=dict(title='ID'), yaxis=dict(title='Total Dislikes'))
    fig_dislikes = go.Figure(data=data_dislikes, layout=layout_dislikes)
    plot_contenidos_dislikes = plot(fig_dislikes, output_type='div', include_plotlyjs=False)

    data_vistas = [go.Bar(x=list(vistas_ordenadas.keys()), y=list(vistas_ordenadas.values()))]
    layout_vistas = go.Layout(title='Contenidos más Vistos', xaxis=dict(title='ID'), yaxis=dict(title='Total Vistas'))
    fig_vistas = go.Figure(data=data_vistas, layout=layout_vistas)
    plot_contenidos_vistas = plot(fig_vistas, output_type='div', include_plotlyjs=False)

    data_compartidos = [go.Bar(x=list(compartidos_ordenados.keys()), y=list(compartidos_ordenados.values()))]
    layout_compartidos = go.Layout(title='Contenidos más Compartidos', xaxis=dict(title='ID'), yaxis=dict(title='Total Compartidos'))
    fig_compartidos = go.Figure(data=data_compartidos, layout=layout_compartidos)
    plot_contenidos_compartidos = plot(fig_compartidos, output_type='div', include_plotlyjs=False)
    
    data_calificaciones = [go.Bar(x=list(calificaciones_ordenadas.keys()), y=list(calificaciones_ordenadas.values()))]
    layout_calificaciones = go.Layout(title='Contenidos mejor Calificados', xaxis=dict(title='ID'), yaxis=dict(title='Calificación'))
    fig_calificaciones = go.Figure(data=data_calificaciones, layout=layout_calificaciones)
    plot_contenidos_calificados = plot(fig_calificaciones, output_type='div', include_plotlyjs=False)


    context = {
        'plot_contenidos_likes': plot_contenidos_likes,
        'plot_contenidos_dislikes': plot_contenidos_dislikes,
        'plot_contenidos_vistas': plot_contenidos_vistas,
        'plot_contenidos_compartidos': plot_contenidos_compartidos,
        'plot_contenidos_calificados': plot_contenidos_calificados
    }
    return render(request, 'graficos/graficos_autor.html', context)
class ReportarContenido(CreateView):
    """
    Comentado 29-11-23
    Esta clase nos permite Reportar un Contenido en estado Publicado, nos presenta un formulario para poner la razon del motivo y enviamos , esto se guarda en un "historial"
    de reportes para que pueda ser visto por el autor del contenido
    class ReportarContenido(CreateView):
    # Vista para crear un reporte
    model = Reporte
    fields = ["texto"]
    template_name = "articulo/reportar_articulo.html"

    def get_context_data(self, **kwargs):
        # Obtiene el titulo y autor del contenido y los agrega al context que usa el template
        context = super().get_context_data(**kwargs)
        cont = Contenido.objects.get(pk=self.kwargs['pk'])
        context['titulo'] = cont.titulo
        context['autor'] = cont.autor.nombres + ', ' + cont.autor.apellidos
        return context
    
    def form_valid(self, form):
        # Completa los campos del formulario y guarda el reporte, luego redirige de vuelta a la pagina del contenido
        form.instance.contenido = Contenido.objects.get(pk=self.kwargs['pk'])
        form.instance.usuario = UsuarioRol.objects.get(username=self.request.user.username)
        response = super(ReportarContenido, self).form_valid(form)
        # Notifica al autor
        mensaje = render_to_string("email-notifs/email_notificacion_reporte.html",
                                            {
                                            'titulo': form.instance.contenido.titulo,
                                            'usuario': form.instance.usuario.username,
                                            'fecha': form.instance.fecha_creacion,
                                            'razon': form.instance.texto,
                                            'urlhost':self.request.get_host(),
                                            'contenidopk':form.instance.contenido.pk})
    
        send_mail(subject="Contenido reportado",
                  message= "Su contenido {form.instance.contenido.titulo} ha sido reportado", 
                    from_email=None,
                        recipient_list=[self.object.contenido.autor.email, 'is2cmseq03@gmail.com'],
                        html_message=mensaje)

        return response
    
    def get_success_url(self) -> str:
        return reverse('detalles_articulo', kwargs={"pk":self.kwargs["pk"]})
    """
    # Vista para crear un reporte
    model = Reporte
    fields = ["texto"]
    template_name = "articulo/reportar_articulo.html"

    def get_context_data(self, **kwargs):
        # Obtiene el titulo y autor del contenido y los agrega al context que usa el template
        context = super().get_context_data(**kwargs)
        cont = Contenido.objects.get(pk=self.kwargs['pk'])
        context['titulo'] = cont.titulo
        context['autor'] = cont.autor.nombres + ', ' + cont.autor.apellidos
        return context
    
    def form_valid(self, form):
        # Completa los campos del formulario y guarda el reporte, luego redirige de vuelta a la pagina del contenido
        form.instance.contenido = Contenido.objects.get(pk=self.kwargs['pk'])
        form.instance.usuario = UsuarioRol.objects.get(username=self.request.user.username)
        response = super(ReportarContenido, self).form_valid(form)
        # Notifica al autor
        mensaje = render_to_string("email-notifs/email_notificacion_reporte.html",
                                            {
                                            'titulo': form.instance.contenido.titulo,
                                            'usuario': form.instance.usuario.username,
                                            'fecha': form.instance.fecha_creacion,
                                            'razon': form.instance.texto,
                                            'urlhost':self.request.get_host(),
                                            'contenidopk':form.instance.contenido.pk})
    
        send_mail(subject="Contenido reportado",
                  message= "Su contenido {form.instance.contenido.titulo} ha sido reportado", 
                    from_email=None,
                        recipient_list=[self.object.contenido.autor.email, 'is2cmseq03@gmail.com'],
                        html_message=mensaje)

        return response
    
    def get_success_url(self) -> str:
        return reverse('detalles_articulo', kwargs={"pk":self.kwargs["pk"]})
    
class ListaReportes(ListView):
    """
    Fecha de documentacion: 28-11-2023
        Permite ver la lista de contenidos reportados
    """
    model = Reporte
    paginate_by = 5
    template_name = "articulo/lista_reportes.html"
    
    def get_queryset(self):
        """
        Fecha de documentacion: 28-11-2023
            Se modifica la funcion para filtrar los reportes por id de contenido
        """
        f = {}
        t = self.request.GET.get('filtro_id')
        if (t is not None and t is not ''):
            f = f | {'contenido__pk': t}
        
        qs = super().get_queryset().filter(contenido__autor__username=self.request.user.username) # Solo carga los reportes enviados al autor del contenido
        return qs.filter(**f).order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        """
        Fecha de documentacion: 07-09-2023
            Se sobreescribe para agregar los criterios de filtrado al contexto de la pagina para ser utilizados en templates
        """
        context = super().get_context_data(**kwargs)
        context["filtro_id"] = self.request.GET.get('filtro_id') or ''
        return context
    
    def post(self, request):
        if request.POST.get('filtro_id') is None:
            return redirect('contenidos_reportados')
        return super(ListaReportes, self)
    
class CrearRol(CreateView, PermissionRequiredMixin, LoginRequiredMixin):
    """
    Fecha Comentario 29-11-2023
    Nos permite crear un nuevo rol , añadiendole permisos personalizados, el creador debe conocer los permios nnecesarios para navegar en el sistema.
    class CrearRol(CreateView, PermissionRequiredMixin, LoginRequiredMixin):
    model = Rol
    fields = ['nombre', 'permisos']
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear Rol"
        context["submitbutton"] = "Guardar nuevo rol"
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super(CrearRol, self).form_valid(form)
        return response
    """
    model = Rol
    fields = ['nombre', 'permisos']
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear Rol"
        context["submitbutton"] = "Guardar nuevo rol"
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super(CrearRol, self).form_valid(form)
        return response
    
class EditarRol(UpdateView, PermissionRequiredMixin, LoginRequiredMixin):
    """
    Comentado 29-11-23
    Esta clase pdoemos editar los permisos que contiene un rol, permitienado hacer  dinamicos los roles
    class EditarRol(UpdateView, PermissionRequiredMixin, LoginRequiredMixin):
    model = Rol
    fields = ['nombre', 'permisos']
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar Rol"
        context["submitbutton"] = "Guardar rol"
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        if form.initial["nombre"] in ["Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado"]:
            raise ValueError("No se permite editar los roles basicos")
        response = super(EditarRol, self).form_valid(form)
        return response
    """
    model = Rol
    fields = ['nombre', 'permisos']
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar Rol"
        context["submitbutton"] = "Guardar rol"
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        if form.initial["nombre"] in ["Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado"]:
            raise ValueError("No se permite editar los roles basicos")
        response = super(EditarRol, self).form_valid(form)
        return response
    
class EliminarRol(UpdateView, PermissionRequiredMixin, LoginRequiredMixin):
    """
    Comentado 29-11-23
    La siguiente vista se creo para que en la vista asignar roles , podamos quitar tambien roles a un usuario , por ejemplo si un usuario tiene el rol autor y se lo queremos quitar
    class EliminarRol(UpdateView, PermissionRequiredMixin, LoginRequiredMixin):
    model = Rol
    fields = []
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Desactivar Rol"
        context["submitbutton"] = "Si, desactivar el rol"
        context["mensaje_eliminacion"] = True
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        if self.object.nombre in ["Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado"]:
            raise ValueError("No se permite eliminar los roles basicos")
        self.object.borrado = True
        response = super(EliminarRol, self).form_valid(form)
        return response
    """
    model = Rol
    fields = []
    template_name = 'crear_rol.html'
    login_url = reverse_lazy('login')
    permission_required = "Vista_administrador"


    def get_success_url(self) -> str:
        return reverse('gestion')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Desactivar Rol"
        context["submitbutton"] = "Si, desactivar el rol"
        context["mensaje_eliminacion"] = True
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        if self.object.nombre in ["Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado"]:
            raise ValueError("No se permite eliminar los roles basicos")
        self.object.borrado = True
        response = super(EliminarRol, self).form_valid(form)
        return response
    
@login_required(login_url="/login")
def seleccionar_rol(request):
    """
    Comentado 29-11-23
    Esta vista se creo para poder asignar roles dentro del sistema , un administrador aqui puede modificar roles de usuarios
        def seleccionar_rol(request):
        if request.method == 'POST':
            rol_id = request.POST.get('rol')
            if rol_id is None:
                raise ValueError("Debe seleccionar un rol")
            if "editar_rol" in request.POST:
                return redirect('editar_rol', pk=rol_id)
            elif "eliminar_rol" in request.POST:
                return redirect('desactivar_rol', pk=rol_id)
        else:
            roles = Rol.objects.all()
            roles = roles.exclude(nombre__in=("Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado")) # No permite modificar los roles basicos
            context = {
                'roles': roles,
            }
            return render(request, 'editar_rol.html', context)
    """
    if request.method == 'POST':
        rol_id = request.POST.get('rol')
        if rol_id is None:
            raise ValueError("Debe seleccionar un rol")
        if "editar_rol" in request.POST:
            return redirect('editar_rol', pk=rol_id)
        elif "eliminar_rol" in request.POST:
            return redirect('desactivar_rol', pk=rol_id)
    else:
        roles = Rol.objects.all()
        roles = roles.exclude(nombre__in=("Administrador", "Autor", "Editor", "Publicador", "Suscriptor", "Autor no moderado")) # No permite modificar los roles basicos
        context = {
            'roles': roles,
        }
        return render(request, 'editar_rol.html', context)

@login_required(login_url="/login")
def pasar_a_borrador_contenido(request,contenido_id):
    """
    Comentado 29-11-23
    Se definio esta funcion para que un autor pueda pasar al estado borrador un contenido que el creo y se encuentra inactivo
    def pasar_a_borrador_contenido(request,contenido_id):
         # Obtén el objeto de contenido basado en algún criterio, como un ID
            contenido = Contenido.objects.get(id=contenido_id)
            contenido.fecha_publicacion = None
            contenido.estado = 'B'
        
            # Guarda el objeto de contenido
            contenido.save()
            nuevo_cambio = HistorialContenido(
                        contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                        cambio=f"El contenido con el Titulo {contenido.titulo} fue enviado a borrador por su autor {contenido.autor.username}. El contenido pasa de estado inactivo a borrador"
                    )
            nuevo_cambio.save()
            mensaje_edicion = render_to_string("email-notifs/email_notificacion_reactivar_autor.html",
                                                    {
                                                    'nombre_editor':contenido.ultimo_editor,
                                                    'nombre_autor':contenido.autor_id,
                                                    'titulo_contenido': contenido.titulo,
                                                    'razon': contenido.razon,
                                                    'urlhost':request.get_host(),
                                                            'contenidopk':contenido.pk})
            

            send_mail(subject="Se ha puesto en borrador un contenido", message=f"Su contenido {contenido.titulo} fue movido de inactivo a borrador",
                        from_email=None,
                            recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                            html_message=mensaje_edicion)

            
            # Redirige al usuario a la vista del editor
            return redirect('vista_autor')    

    Como podemos ver se cambia de estado I a B , se guarda en el historial el movimiento y se motifica de esto al autor mediante su correo electronico        
    """
    # Obtén el objeto de contenido basado en algún criterio, como un ID
    contenido = Contenido.objects.get(id=contenido_id)
    contenido.fecha_publicacion = None
    contenido.estado = 'B'
   
    # Guarda el objeto de contenido
    contenido.save()
    nuevo_cambio = HistorialContenido(
                contenido=contenido,  # Asigna la instancia de Contenido, no el ID
                cambio=f"El contenido con el Titulo {contenido.titulo} fue enviado a borrador por su autor {contenido.autor.username}. El contenido pasa de estado inactivo a borrador"
            )
    nuevo_cambio.save()
    mensaje_edicion = render_to_string("email-notifs/email_notificacion_reactivar_autor.html",
                                            {
                                            'nombre_editor':contenido.ultimo_editor,
                                            'nombre_autor':contenido.autor_id,
                                            'titulo_contenido': contenido.titulo,
                                            'razon': contenido.razon,
                                            'urlhost':request.get_host(),
                                                    'contenidopk':contenido.pk})
    

    send_mail(subject="Se ha puesto en borrador un contenido", message=f"Su contenido {contenido.titulo} fue movido de inactivo a borrador",
                from_email=None,
                    recipient_list=[UsuarioRol.objects.get(id=contenido.autor_id).email, 'is2cmseq03@gmail.com', ],
                    html_message=mensaje_edicion)

    
    # Redirige al usuario a la vista del editor
    return redirect('vista_autor')    
