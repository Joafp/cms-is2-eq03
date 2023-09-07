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
    model = UsuarioRol
    fields = ["username", "email", "nombres", "apellidos", "numero", "usuario_activo", "usuario_administrador", "roles" ]
    template_name = "administrador/usuariorol_update_form.html"
    success_url = reverse_lazy("listaUsuarios")
    permission_required = "Editar usuarios"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'].fields['numero'].label = 'Telefono'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Actualizacion exitosa del usuario {form.cleaned_data['username']}.")
        return super(vista_editar_usuario, self).form_valid(form)

class vista_lista_usuarios(CustomPermissionRequiredMixin, ListView):
    model = UsuarioRol
    paginate_by = 25
    template_name = "administrador/lista_usuarios.html"
    permission_required = "Ver usuarios"
    
    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["filtro_username"] = self.request.GET.get('filtro_username') or ''
        context["filtro_email"] = self.request.GET.get('filtro_email') or ''
        return context

class vista_inactivar_cuenta(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UsuarioRol
    fields = ["usuario_activo"]
    template_name = "usuario/inactivar.html"
    success_url = reverse_lazy("MenuPrincipal")
    login_url = reverse_lazy('login')
    redirect_field_name = "redirect_to"
   
    def form_valid(self, form):
        if form.cleaned_data.get('usuario_activo') is True:
            messages.warning(self.request, "No se ha inactivado la cuenta")
            return redirect(reverse_lazy('MenuPrincipal'))
        messages.success(self.request, f"Se ha inactivado la cuenta del usuario {self.request.user.username}.")
        self.request.user.is_active = False
        self.request.user.save()
        logout(self.request)
        return super(vista_inactivar_cuenta, self).form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'].fields['usuario_activo'].label = 'Cuenta activa'
        return context
    
    def test_func(self):
        loginid = UsuarioRol.objects.get(username=self.request.user.username).id
        updateid = self.get_object().id
        return  loginid == updateid
   

class vista_recuperar_password(SuccessMessageMixin, PasswordResetView):
    template_name = "usuario/recuperar_password.html"
    email_template_name = 'usuario/recuperar_password_email.html'
    subject_template_name = 'usuario/recuperar_password_subject'
    success_message = "Se enviara un email a la direccion ingresada si esta asociada a una cuenta. Si no recibe el email, revise su carpeta de spam."
    success_url = reverse_lazy('MenuPrincipal')

def redirgirInactivar(request):
    return redirect(reverse_lazy('inactivarCuenta', kwargs={'pk':UsuarioRol.objects.get(username=request.user.username).id}))