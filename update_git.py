import subprocess
import sys
import os

def update_git():
    # Asegurarnos de que estamos en el directorio correcto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Mensaje de commit personalizado o por defecto
    commit_msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Auto-update: Syncing project and transparent icons"

    try:
        print(f"--- Sincronizando repositorio en: {current_dir} ---")
        
        # 1. Agregar todos los cambios
        subprocess.run(["git", "add", "."], check=True)
        print("✓ Cambios agregados.")
        
        # 2. Hacer commit
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print(f"✓ Commit realizado: '{commit_msg}'")
        
        # 3. Empujar al servidor
        # He visto que en pasos anteriores se usó 'origin' y 'main'
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✓ Repositorio actualizado en GitHub con éxito.")
        
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            print("(!) No hay cambios nuevos para subir.")
        else:
            print(f"(!) Error al ejecutar comando de Git: {e}")
    except Exception as ex:
        print(f"(!) Error inesperado: {ex}")

if __name__ == "__main__":
    update_git()
