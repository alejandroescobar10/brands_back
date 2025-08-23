# 1) Clonar y entrar

git clone [<tu_repo.git>](https://github.com/alejandroescobar10/brands_back.git)
cd brands_back

# 2) Crear/activar venv

python -m venv .venv
.venv\Scripts\Activate # (PowerShell)

# 3) Instalar dependencias

pip install -r requirements.txt

# si no tienes requirements.txt, ver sección de Dependencias

# 4) Variables de entorno (.env en la raíz)

# ver ejemplo abajo

# 5) Ejecutar

python -m uvicorn index:app --reload --log-level debug

# Abre: http://127.0.0.1:8000/docs y http://127.0.0.1:8000/api/health
