"""
    Fecha de documentacion: 07-09-2023
    Contiene las vistas necesarias para que el administrador edite la informacion de usuarios,
    Tambien las vistas para que un usuario recupere su contraseña y para inactivar su cuenta
"""
from typing import Any, Dict, Optional, Type
from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from GestionCuentas.models import UsuarioRol
from django.contrib import messages
from core.views import CustomPermissionRequiredMixin
from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin


class vista_editar_usuario(CustomPermissionRequiredMixin, UpdateView):
    """
    Fecha de documentacion: 07-09-2023
    Permite que el administrador edite la informacion de un usuario a traves de un formulario,
    el formulario se crea a partir del modelo GestionCuentas.models.UsuarioRol:
    model = UsuarioRol
    utilizando los campos especificados en fields:
    fields = ["username", "email", "nombres", "apellidos", "numero", "usuario_activo", "usuario_administrador", "roles" ]
    Ademas se sobreescribio el metodo form_valid(self,form) para  enviar una notificacion al navegador cuando se completa el proceso correctamente
    Ademas se requiere que el usuario cuente con el permiso especificado en el atributo:
    permission_required = "Editar usuarios"
    """
    model = UsuarioRol
    fields = ["username", "email", "nombres", "apellidos", "numero", "usuario_activo", "usuario_administrador", "roles" ]
    template_name = "administrador/usuariorol_update_form.html"
    success_url = reverse_lazy("listaUsuarios")
    permission_required = "Editar usuarios"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Fecha de documentacion: 07-09-2023
            Modificado para mostrar la etiqueta correcta
            context = super().get_context_data(**kwargs)
            context['form'].fields['numero'].label = 'Telefono'
        """
        context = super().get_context_data(**kwargs)
        context['form'].fields['numero'].label = 'Telefono'
        return context

    def form_valid(self, form):
        """
        Fecha de documentacion: 07-09-2023
            Modificado para enviar un mensaje de finalizacion
            messages.success(self.request, f"Actualizacion exitosa del usuario {form.cleaned_data['username']}.")
            return super(vista_editar_usuario, self).form_valid(form)
        """
        messages.success(self.request, f"Actualizacion exitosa del usuario {form.cleaned_data['username']}.")
        return super(vista_editar_usuario, self).form_valid(form)

class vista_lista_usuarios(CustomPermissionRequiredMixin, ListView):
    """
    Fecha de documentacion: 07-09-2023
        Permite al administrador ver una lista de los usuarios para editar y filtrar por nombre o email
        Se muestran los usuarios en una vista paginada
        paginate_by = 25
        Y se requiere el permiso
        permission_required = "Ver usuarios"
    """
    model = UsuarioRol
    paginate_by = 25
    template_name = "administrador/lista_usuarios.html"
    permission_required = "Ver usuarios"
    
    def get_queryset(self):
        """
        Fecha de documentacion: 07-09-2023
            Se modifica la funcion para filtrar los usuarios con el nombre de usuario y contraseña que se especifiquen en la pagina
            Para el filtrado se utilizan los argumentos username__icontains y email__icontains en conjuncion, 
            por lo que solo se mostraran usuarios si su username y email contienen como substring los argumentos, ignorando casing y tambien argumentos nulos
        """
        f = {}
        t = self.request.GET.get('filtro_username')
        if (t is not None):
            f = f | {'username__icontains': t}
        
        t = self.request.GET.get('filtro_email')
        if (t is not None):
            f = f | {'email__icontains': t}
        
        qs = super().get_queryset()
        return qs.filter(**f)
    
    def get_context_data(self, **kwargs):
        """
        Fecha de documentacion: 07-09-2023
            Se sobreescribe para agregar los criterios de busqueda al contexto de la pagina para ser utilizados en templates
            context["filtro_username"] = self.request.GET.get('filtro_username') or ''
            context["filtro_email"] = self.request.GET.get('filtro_email') or ''
        """
        context = super().get_context_data(**kwargs)
        context["filtro_username"] = self.request.GET.get('filtro_username') or ''
        context["filtro_email"] = self.request.GET.get('filtro_email') or ''
        return context

class vista_inactivar_cuenta(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Fecha de documentacion: 07-09-2023
        Crea la vista para inactivar una cuenta, exige que el usuario este logueado y verifica que sea su cuenta la que se esta inactivando,
        Antes de inactivar se verifica que el usuario haya desmarcado una casilla y oprimido el boton de inactivar
        Luego se marca la cuenta como inactivada y se hace logout al usuario
        Finalmente se envia la notificacion de finalizacion y se redirige a la pagina principal
        Utiliza el modelo UsuarioRol y su campo:
        model = UsuarioRol
        fields = ["usuario_activo"]
    """
    model = UsuarioRol
    fields = ["usuario_activo"]
    template_name = "usuario/inactivar.html"
    success_url = reverse_lazy("MenuPrincipal")
    login_url = reverse_lazy('login')
    redirect_field_name = "redirect_to"
   
    def form_valid(self, form):
        """
        Fecha de documentacion: 07-09-2023
            Verifica que se haya desmarcado la casilla de cuenta activa antes de enviar la solicitud
            Si el proceso es correcto, envia un mensaje y actualiza el estado del usuario a inactivo antes de cerrar su sesion:
            messages.success(self.request, f"Se ha inactivado la cuenta del usuario {self.request.user.username}.")
            self.request.user.is_active = False
            self.request.user.save()
            logout(self.request)
            Envia un mensaje en caso contrario:
            messages.warning(self.request, "No se ha inactivado la cuenta")
            return redirect(reverse_lazy('MenuPrincipal'))
        """
        if form.cleaned_data.get('usuario_activo') is True:
            messages.warning(self.request, "No se ha inactivado la cuenta")
            return redirect(reverse_lazy('MenuPrincipal'))
        messages.success(self.request, f"Se ha inactivado la cuenta del usuario {self.request.user.username}.")
        self.request.user.is_active = False
        self.request.user.save()
        logout(self.request)
        return super(vista_inactivar_cuenta, self).form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Fecha de documentacion: 07-09-2023
            Modifica el contexto para mostrar una label mas adecuada
            context['form'].fields['usuario_activo'].label = 'Cuenta activa'
        """
        context = super().get_context_data(**kwargs)
        context['form'].fields['usuario_activo'].label = 'Cuenta activa'
        return context
    
    def test_func(self):
        """
        Fecha de documentacion: 07-09-2023
            Verifica que el usuario que esta intentando inactivar es el que esta logueado comparando el id del usuario logueado con el id del formulario
        """
        loginid = UsuarioRol.objects.get(username=self.request.user.username).id
        updateid = self.get_object().id
        return  loginid == updateid
   

class vista_recuperar_password(SuccessMessageMixin, PasswordResetView):
    """
    Fecha de documentacion: 07-09-2023
        Implementa la vista PasswordResetView de django
        template_name es el template del formulario de solicitud de recuperacion
        template_name = "usuario/recuperar_password.html"
        email_template_name contiene el template del email a enviar
        email_template_name = 'usuario/recuperar_password_email.html'
        subject_template_name contiene el asunto del email
        subject_template_name = 'usuario/recuperar_password_subject'
        success message contiene la notificacion que se vera en la pagina
        success_message = "Se enviara un email a la direccion ingresada si esta asociada a una cuenta. Si no recibe el email, revise su carpeta de spam."
        success_url redirige a la pagina principal luego de enviar la solicitud
        success_url = reverse_lazy('MenuPrincipal')
    """
    template_name = "usuario/recuperar_password.html"
    email_template_name = 'usuario/recuperar_password_email.html'
    subject_template_name = 'usuario/recuperar_password_subject'
    success_message = "Se enviara un email a la direccion ingresada si esta asociada a una cuenta. Si no recibe el email, revise su carpeta de spam."
    success_url = reverse_lazy('MenuPrincipal')

def redirgirInactivar(request):
    """
    Fecha de documentacion: 07-09-2023
        Obtiene el id del usuario para redirigirlo a la url correcta de inactivacion
    """
    return redirect(reverse_lazy('inactivarCuenta', kwargs={'pk':UsuarioRol.objects.get(username=request.user.username).id}))