import random
import string
from app.db import base_class, session


# lists to create random names
first_list=['Alison' 'Ashley' 'Barbara' 'Benjamin' 'Bernice' 'Betsy' 'Bonnie'
                'Brandon' 'Brian' 'Brittany' 'Candy' 'Catherine' 'Cheryl' 'Christina'
                'Clara' 'Clarence' 'Cythia' 'Diane' 'Dianne' 'Donna' 'Edward' 'Gary'
                'Gladys' 'Gudrun' 'Hazel' 'Henry' 'Hugo' 'Jamie' 'Jay' 'Jill' 'John'
                'Katherine' 'Kellie' 'Kelly' 'Ken' 'Leon' 'Lillie' 'Lori' 'Luke' 'Marion'
                'Michell' 'Nicole' 'Robert' 'Robin' 'Ruth' 'Stanley' 'Steven' 'Thomas'
                'Toni']
    
last_list=['Baylock' 'Benites' 'Blevins' 'Bossert' 'Bowen' 'Campbell' 'Cartwright'
                'Cayer' 'Corradino' 'Desrochers' 'Doggett' 'Drain' 'Elizondo' 'Enos'
                'Gardner' 'Gill' 'Hagadone' 'Hernandez' 'Hunt' 'King' 'Kirk' 'Larose'
                'Licea' 'Malone' 'Martin' 'Massaro' 'Mcelvain' 'Moore' 'Paez' 'Phang'
                'Randle' 'Read' 'Redding' 'Rich' 'Rioux' 'Rivera' 'Rodriguez' 'Rollins'
                'Russell' 'Sawyer' 'Shaw' 'Shortridge' 'Spurbeck' 'Stumpe' 'Tiburcio'
                'Tran' 'Vest' 'Villa' 'Waters' 'Watts']

email_list=['gmail','hotmail','yahoo','protonmail','outlook','aol','zoho','icloud','gmx'] 

# random name
def random_name():
    return (random.choices(first_list), random.choises(last_list))

# random generators for fake data
def random_generator(random_list: list):
    return "".join(random.choices(random_list))

def random_email(username):
    return f"{username}@{random_generator(email_list)}.com"

def random_username(first,last):
    return f"{first}_{last}{random.randint(0,100)}"

# for fake data, can be incorporated into app.utils instead 
def create_database():
    return base_class.Base.metadata.create_all(bind=session.engine)

# to get local DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()
