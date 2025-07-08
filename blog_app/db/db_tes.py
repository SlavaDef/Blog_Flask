from blog_app.db.service import UserDatabase

db = UserDatabase()


db.create_user("First", "sld@gmail.com", '1234')
db.create_user("First2", "sld2@gmail.com", '12345')

for user in db.select_all():
   print(user)