from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from GestionCuentas.models import UsuarioRol
from django.shortcuts import get_object_or_404

@login_required
@permission_required("Vista administrador", raise_exception=True)
def oldvista_editar_usuario(request):
    # if request.method == 'POST':
            # return ...
    # else:
    return render(request, 'administrador/editarusuario.html')


class vista_editar_usuario(UpdateView):
    model = UsuarioRol
    fields = ["username", "email", "nombres", "apellidos", "numero", "usuario_activo", "usuario_administrador", "roles", "password"]
    template_name = "administrador/usuariorol_update_form.html"
    success_url = reverse_lazy("MenuPrincipal")

class vista_lista_usuarios(ListView):
    model = UsuarioRol
    paginate_by = 25
    template_name = "administrador/lista_usuarios.html"

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

