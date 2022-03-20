import random

# lists to create random names
first_list=['Alison', 'Ashley', 'Barbara', 'Benjamin', 'Bernice', 'Betsy', 'Bonnie',
                'Brandon', 'Brian', 'Brittany', 'Candy', 'Catherine', 'Cheryl', 'Christina',
                'Clara', 'Clarence', 'Cythia', 'Diane', 'Dianne', 'Donna', 'Edward', 'Gary',
                'Gladys', 'Gudrun', 'Hazel', 'Henry', 'Hugo', 'Jamie' 'Jay', 'Jill', 'John',
                'Katherine', 'Kell,ie', 'Kelly', 'Ken', 'Leon', 'Lillie', 'Lori', 'Luke', 'Marion',
                'Michell', 'Nicole', 'Robert', 'Robin', 'Ruth', 'Stanley', 'Steven', 'Thomas',
                'Toni']
    
last_list=['Baylock', 'Benites', 'Blevins', 'Bossert', 'Bowen', 'Campbell', 'Cartwright',
                'Cayer', 'Corradino', 'Desrochers', 'Doggett', 'Drain', 'Elizondo', 'Enos',
                'Gardner', 'Gill', 'Hagadone', 'Hernandez', 'Hunt', 'King', 'Kirk', 'Larose',
                'Licea', 'Malone', 'Martin', 'Massaro', 'Mcelvain', 'Moore', 'Paez', 'Phang',
                'Randle', 'Read', 'Redding', 'Rich', 'Rioux', 'Rivera', 'Rodriguez', 'Rollins',
                'Russell', 'Sawyer', 'Shaw', 'Shortridge', 'Spurbeck', 'Stumpe', 'Tiburcio',
                'Tran', 'Vest', 'Villa', 'Waters', 'Watts']

email_list=['gmail','hotmail','yahoo','protonmail','outlook','aol','zoho','icloud','gmx'] 

# random name
def random_name():
    first = random.choice(first_list)
    last = random.choice(last_list)
    return (first, last)


def random_email(username):
    email = f"{username}@{random.choice(email_list)}.com"
    return email

def random_username(first, last):
    username = f"{first}_{last}{random.randint(0,100)}"
    return username


def random_user_id(x):
    user_id_lst = random.sample(range(1, 100), x)
    return user_id_lst



