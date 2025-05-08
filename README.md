# DESD

cloud link : http://paulamie.pythonanywhere.com 

you can access this cloud link on any machine 


DOCKER SETTINGS!!!


# Remove old containers + volume to avoid conflicts
docker-compose down -v

# Start fresh containers with the new image
docker-compose up --build

# To migrate the information 
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate




