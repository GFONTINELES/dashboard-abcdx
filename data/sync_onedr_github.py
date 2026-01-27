import shutil
import os
import subprocess
from datetime import datetime

# 🔹 ORIGEM (OneDrive)
ORIGEM = r"C:\Users\Ferreira\OneDrive\CIG-CONTROLADORIA\3_third_task_abcdx_com_estoque"

# 🔹 DESTINO (repositório GitHub local)
DESTINO = r"C:\Users\Ferreira\dashboard-abcdx\data"

# Limpa destino
for root, dirs, files in os.walk(DESTINO):
    for file in files:
        os.remove(os.path.join(root, file))

# Copia tudo
for loja in os.listdir(ORIGEM):
    origem_loja = os.path.join(ORIGEM, loja)
    destino_loja = os.path.join(DESTINO, loja)

    if os.path.isdir(origem_loja):
        os.makedirs(destino_loja, exist_ok=True)

        for arquivo in os.listdir(origem_loja):
            if arquivo.endswith(".parquet"):
                shutil.copy2(
                    os.path.join(origem_loja, arquivo),
                    os.path.join(destino_loja, arquivo)
                )

# Git commit automático
subprocess.run(["git", "add", "."])
subprocess.run([
    "git", "commit",
    "-m", f"Atualização automática {datetime.now().strftime('%Y-%m-%d %H:%M')}"
])
subprocess.run(["git", "push"])

print("✅ Sincronização concluída.")
