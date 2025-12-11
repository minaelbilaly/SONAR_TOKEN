FROM python:3.9

WORKDIR /app

# On copie les fichiers du dossier "api" dans l'image
COPY api/ .

# Installer Flask
RUN pip install flask

EXPOSE 5000

CMD ["python", "app.py"]
