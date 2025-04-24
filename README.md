# DESD

DOCKER SETTINGS!!!


# Remove old containers + volume to avoid conflicts
docker-compose down -v

# Start fresh containers with the new image
docker-compose up --build

# To migrate the information 
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate




List

#### validate past events do not show WORKS
### Get the community requests to show up on the filter WORKS
### Get the community requests if approved to come up in communities tab WORKS
### Email system WORKS
### Fix community card styling add the interest tab in the card 
### Community requests should show if it is pending/approved/rejected add that 
### join community tab/leave 
### add external eventAPI thing so it can work to another page
### add filters for that maybe leave it if not needed 

