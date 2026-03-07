#!/usr/bin/env python3
"""Lanza un servidor HTTP local y abre `Juego01.html` en el navegador.

Ejemplo:
  python launch_game.py
  python launch_game.py --file Juego01.html --port 8080
"""
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from pathlib import Path
import webbrowser
import argparse
import threading
import sys


def run_server(directory: Path, port: int):
    handler = SimpleHTTPRequestHandler
    class _Server(ThreadingTCPServer):
        allow_reuse_address = True

    old_cwd = Path.cwd()
    try:
        import os
        os.chdir(str(directory))
        with _Server(("127.0.0.1", port), handler) as httpd:
            sa = httpd.socket.getsockname()
            print(f"Servidor en http://{sa[0]}:{sa[1]} sirviendo: {directory}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDeteniendo servidor...")
                httpd.shutdown()
    finally:
        os.chdir(str(old_cwd))


def main():
    parser = argparse.ArgumentParser(description="Lanza Juego01.html con servidor local")
    parser.add_argument("--file", "-f", help="Nombre del fichero HTML a abrir (por defecto Juego01.html)")
    parser.add_argument("--port", "-p", type=int, default=0, help="Puerto (0 para elegir uno libre)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent

    target_name = args.file if args.file else "Juego01.html"
    target = script_dir / target_name
    if not target.exists():
        print(f"No se encontró {target_name} en: {script_dir}")
        print("Asegúrate de ejecutar el script desde la carpeta correcta.")
        sys.exit(1)

    port = args.port
    if port == 0:
        import socket
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()

    server_thread = threading.Thread(target=run_server, args=(script_dir, port), daemon=True)
    server_thread.start()

    from urllib.parse import quote
    url = f"http://127.0.0.1:{port}/{quote(target.name)}"
    print(f"Abriendo en navegador: {url}")
    webbrowser.open(url)

    try:
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        print("Interrumpido por usuario. Saliendo...")


if __name__ == '__main__':
    main()
