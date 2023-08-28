#! /bin/bash
username=joaquin
carpetaproyecto=/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms
gunicorn=/home/joaquin/Escritorio/Proyectois2/venv/bin/gunicorn

sudo cat > /etc/systemd/system/gunicorn.socket << EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

sudo cat > /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$username
Group=www-data
WorkingDirectory=$carpetaproyecto
ExecStart=$gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          cms.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket