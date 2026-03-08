import subprocess
import sys
import os

def update_git():
    # Asegurarnos de que estamos en el directorio correcto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Mensaje de commit personalizado o por defecto
    if len(sys.argv) > 1:
        # Usamos un generador para evitar el error de tipado con rebanadas (slice) si el linter es estricto
        commit_msg = " ".join(sys.argv[i] for i in range(1, len(sys.argv)))
    else:
        commit_msg = "Auto-update: Syncing project and cleaning up MCP folders"

    try:
        print(f"--- Sincronizando repositorio en: {current_dir} ---")
        
        # 0. Desincronizar carpetas que ya no deben estar en git (mcp-supabase, mcp-supabases)
        folders_to_unsync = ["mcp-supabase", "mcp-supabases"]
        for folder in folders_to_unsync:
            try:
                # Intentamos quitar de la caché de git sin borrar archivos locales
                # Redirigimos stderr para no mostrar errores molestos si la carpeta no está en el índice
                subprocess.run(["git", "rm", "-r", "--cached", folder], 
                               capture_output=True, text=True, check=False)
            except Exception:
                pass

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
