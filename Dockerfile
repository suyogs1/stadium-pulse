FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Streamlit-specific configurations for Cloud Run
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8080

# Ensure startup script is executable
RUN chmod +x scripts/start.sh

# Run the startup sequence (Tests -> App)
CMD ["sh", "scripts/start.sh"]
