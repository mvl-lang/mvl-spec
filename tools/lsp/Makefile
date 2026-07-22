# mvl-lsp — dev commands
#
#   make install   Set up venv + install mvl-lsp with test extras (idempotent)
#   make run       Send an LSP initialize request and print the response — proves the server is alive
#   make serve     Start mvl-lsp on stdio (blocks, waiting for an editor to talk to it — normal)
#   make test      Run the smoke tests
#   make clean     Remove the venv

VENV := .venv
PY := $(VENV)/bin/python
LSP := $(VENV)/bin/mvl-lsp

.PHONY: install run serve test clean

install: $(LSP)

$(LSP):
	uv venv $(VENV)
	VIRTUAL_ENV=$(CURDIR)/$(VENV) uv pip install -e ".[test]"

run: install
	@echo "── Sending LSP initialize request to mvl-lsp ─────────────────────"
	@$(PY) -c 'import json, subprocess, time; \
msg = json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"processId":None,"rootUri":None,"capabilities":{}}}); \
init = f"Content-Length: {len(msg)}\r\n\r\n{msg}".encode(); \
p = subprocess.Popen(["$(LSP)"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE); \
p.stdin.write(init); p.stdin.flush(); time.sleep(1); p.stdin.close(); \
out, err = p.communicate(timeout=5); \
print("── stderr (startup banner) ──"); print(err.decode(errors="replace")); \
print("── stdout (LSP response) ──"); print(out.decode(errors="replace")); \
print(f"── exit: {p.returncode} ──")'

serve: install
	@echo "── Starting mvl-lsp on stdio. It will block waiting for LSP JSON-RPC. ──"
	@echo "── This is normal. Editors spawn this process; humans use \`make run\`. ──"
	@$(LSP)

test: install
	$(PY) -m pytest tests/ -v

clean:
	rm -rf $(VENV)
