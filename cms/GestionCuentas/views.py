from typing import Any, Dict, Optional, Type
from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from GestionCuentas.models import UsuarioRol
from django.contrib import messages
from core.views import CustomPermissionRequiredMixin
from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache

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

@never_cache
@login_required
def vista_inactivar_cuenta(request):
    if (request.method == 'POST'):
        # Verificar confirmacion
        verificado = None
        if (verificado):
            # desactivar...
            pass
            logout(request)
            return redirect('MenuPrincipal')
        else:
            #mostrar mensaje de error
            pass
    else: 
        # Mostrar form
        form = None
    return render(request, "usuario/inactivar.html", form)

@never_cache
@login_required
def vista_recuperar_password(request):
    if (request.method == 'POST'):
        # Verificar confirmacion
        verificado = None
        if (verificado):
            # enviar por correo
            # notificar en pagina
            # redirigir al login
            pass
        else:
            #mostrar mensaje de error
            pass
    else: 
        # Mostrar form
        form = None
    return render(request, "usuario/inactivar.html", form)