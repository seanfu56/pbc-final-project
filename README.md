# pbc-final-project

## install

```bash
git clone https://github.com/seanfu56/pbc-final-project.git
```

## environment setting

```bash
conda create -n pbc-final python=3.9
conda activate pbc-final
pip install -r requirements.txt
```

## run the program

Use two terminals concurrently.

Terminal 1 (backend)
```bash
python backend/admin.py
python backend/server.py
```

Terminal 2 (frontend)
```bash
python frontend/app.py
```

The existing users and their passwords can be found in `backend/admin.py`.