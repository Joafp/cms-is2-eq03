import subprocess

if __name__ == "__main__":
    script_path = "/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms/django_pydoc.py"
    modules = ["core.views", "core.forms", "core.tests","core.models","core.urls","core.apps","core.admin"
            ,"GestionCuentas.views","GestionCuentas.urls","GestionCuentas.tests","GestionCuentas.models" 
            ,"login.views","login.urls","login.tests","login.models","login.forms" ]
    
    for module in modules:
        command = f"python3 {script_path} -w {module}"
        subprocess.call(command, shell=True)


