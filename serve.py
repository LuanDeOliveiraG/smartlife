import argparse
import http.server
import socketserver
import ssl
import sys

try:
    import cgitb
    cgitb.enable()
except ModuleNotFoundError:
    print("Aviso: 'legacy-cgi' não instalado. Erros detalhados do CGI não serão exibidos.")

def iniciar_servidor():
    parser = argparse.ArgumentParser(description="Servidor HTTP CGI")
    parser.add_argument("port", type=int, nargs="?", default=8000, help="Porta do servidor (padrão: 8000)")
    args = parser.parse_args()

    # Configura o manipulador CGI
    handler = http.server.CGIHTTPRequestHandler
    handler.cgi_directories = ["/cgi-bin"]

    # Cria o servidor TCP seguro contra vazamento de portas (allow_reuse_address)
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        # Configuração Moderna de SSL (substituta do wrap_socket)
        if args.port == 4443:
            try:
                contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                contexto.load_cert_chain(certfile="localhost.pem", keyfile="localhost.pem")
                httpd.socket = contexto.wrap_socket(httpd.socket, server_side=True)
                print("🔒 Modo HTTPS ativado.")
            except FileNotFoundError:
                print("❌ Erro: Arquivo 'localhost.pem' não encontrado. Iniciando em HTTP normal.")

        print(f"🚀 Servidor CGI rodando na porta {args.port}...")
        print(f"Acesse: http{'s' if args.port == 4443 else ''}://localhost:{args.port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor encerrado pelo usuário.")

if __name__ == "__main__":
    iniciar_servidor()