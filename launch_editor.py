#!/usr/bin/env python3
"""Lanza un servidor HTTP local y abre el editor HTML en el navegador.

Uso:
  python launch_editor.py            # busca `editor.html` o `amigos_editor.html`
  python launch_editor.py --file editor.html --port 8000
"""
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from pathlib import Path
import webbrowser
import argparse
import threading
import sys


def find_target(path: Path, candidates):
    for name in candidates:
        p = path / name
        if p.exists():
            return p
    return None


def run_server(directory: Path, port: int):
    handler = SimpleHTTPRequestHandler
    class _Server(ThreadingTCPServer):
        allow_reuse_address = True

    # change cwd so SimpleHTTPRequestHandler serves from directory
    old_cwd = Path.cwd()
    try:
        import os
        os.chdir(str(directory))
        with _Server(("127.0.0.1", port), handler) as httpd:
            sa = httpd.socket.getsockname()
            print(f"Servidor HTTP en http://{sa[0]}:{sa[1]} serving: {directory}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDeteniendo servidor...")
                httpd.shutdown()
    finally:
        os.chdir(str(old_cwd))


def main():
    parser = argparse.ArgumentParser(description="Lanza editor HTML con servidor local")
    parser.add_argument("--file", "-f", help="Nombre de fichero HTML a abrir (por defecto busca editor.html)")
    parser.add_argument("--port", "-p", type=int, default=0, help="Puerto (0 para elegir uno libre)")
    args = parser.parse_args()

    # carpeta donde está este script
    script_dir = Path(__file__).resolve().parent

    candidates = []
    if args.file:
        candidates.append(args.file)
    candidates.extend(["editor.html", "amigos_editor.html", "amigos-editor.html", "amigos.sqlite.html"])

    target = find_target(script_dir, candidates)
    if not target:
        print("No se encontró ningún fichero HTML candidato en:", script_dir)
        print("Buscó:", ", ".join(candidates))
        sys.exit(1)

    # If port 0, find a free port by binding to 0 in a temp socket
    port = args.port
    if port == 0:
        import socket
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(script_dir, port), daemon=True)
    server_thread.start()

    # build URL and open
    from urllib.parse import quote
    url = f"http://127.0.0.1:{port}/{quote(target.name)}"
    print(f"Abriendo en navegador: {url}")
    webbrowser.open(url)

    try:
        # keep main thread alive while server runs
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        print("Interrumpido por usuario. Saliendo...")


if __name__ == '__main__':
    main()
