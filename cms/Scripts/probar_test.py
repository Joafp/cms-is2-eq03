import subprocess

if __name__ == "__main__":
    script_path = "/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms/manage.py"
    modules = ["core.tests","login.tests","GestionCuentas.tests" ]
    
    for module in modules:
        command = f"python3 {script_path} test {module}"
        subprocess.call(command, shell=True)