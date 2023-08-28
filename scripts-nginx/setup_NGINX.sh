#! /bin/bash
carpetaproyecto=/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms
serverIP=localhost

sudo cat > /etc/nginx/sites-available/cmsis2e03 << EOF
server {
    listen 80;
    server_name $serverIP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $carpetaproyecto;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix/run/gunicorn.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/cmsis2eq03 /etc/nginx/sites-enabled

sudo systemctl restart nginx