echo "Setting local environment variables..."

# BASIC CONFIG

export DEBUG=on
export SECRET_KEY="mxi_5qb4s@zx+7zq(*bi2^^av=sps=22f7)6_%r9su2vpm8^w3"
export LOG_LEVEL="INFO"
export CORS_ORIGIN_WHITELIST="http://localhost:3000"
export ALLOWED_HOSTS="localhost,127.0.0.1"
export AWS_REGION_NAME=""

# SUPERUSER DETAILS

export ADMIN_EMAIL_ADDRESS=test@thisisadmin.com
export ADMIN_PASSWORD=thisispassword

# AWS AUTH

export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""

# AWS LOGGING

export AWS_LOG_GROUP=""
export AWS_LOG_STREAM=""

# WORKER CONFIG

export AWS_WORKER_QUEUE=""


if [ $1 == runserver__ ]
then
    echo "Running Tailwind build..."
    cd theme/static && npm i && cd ../.. && python manage.py tailwind build
fi

echo "Running python manage.py $1"

python manage.py $1
