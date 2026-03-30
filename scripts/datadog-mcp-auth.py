#!/usr/bin/env python3
"""
Datadog MCP OAuth 토큰 발급 스크립트
출력된 JSON을 GitHub Secret DATADOG_MCP_TOKEN 에 저장하세요.

Usage: python3 datadog-mcp-auth.py
"""

import json, secrets, hashlib, base64, urllib.parse, urllib.request
import http.server, threading, webbrowser

DISCOVERY_URL = "https://mcp.datadoghq.com/.well-known/oauth-authorization-server"
REDIRECT_PORT = 8766
REDIRECT_URI  = f"http://localhost:{REDIRECT_PORT}/callback"


def fetch_json(url, data=None, headers={}):
    req = urllib.request.Request(url, data=data, headers=headers)
    return json.loads(urllib.request.urlopen(req).read())


def pkce_pair():
    verifier  = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def wait_for_code():
    code = {}
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            code["value"] = params.get("code")
            self.send_response(200); self.end_headers()
            self.wfile.write("인증 완료 — 터미널로 돌아가세요".encode())
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        def log_message(self, *a): pass
    server = http.server.HTTPServer(("", REDIRECT_PORT), Handler)
    server.serve_forever()
    return code["value"]


def main():
    disc = fetch_json(DISCOVERY_URL)

    # Dynamic Client Registration
    reg = fetch_json(disc["registration_endpoint"],
        data=json.dumps({"client_name": "github-actions",
            "redirect_uris": [REDIRECT_URI],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none"}).encode(),
        headers={"Content-Type": "application/json"})
    client_id = reg["client_id"]

    # PKCE + 브라우저 열기
    verifier, challenge = pkce_pair()
    auth_url = disc["authorization_endpoint"] + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": challenge, "code_challenge_method": "S256",
        "state": secrets.token_hex(8)})

    print("브라우저에서 Datadog 로그인 후 인증을 완료하세요...")
    webbrowser.open(auth_url)
    code = wait_for_code()

    # Token exchange
    tok = fetch_json(disc["token_endpoint"],
        data=urllib.parse.urlencode({"grant_type": "authorization_code",
            "client_id": client_id, "redirect_uri": REDIRECT_URI,
            "code": code, "code_verifier": verifier}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"})

    result = json.dumps({"client_id": client_id, "refresh_token": tok["refresh_token"]})
    print(f"\nDATADOG_MCP_TOKEN:\n{result}")


if __name__ == "__main__":
    main()
