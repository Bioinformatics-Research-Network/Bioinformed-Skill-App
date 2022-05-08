import random

random.seed(42)


# lists to create fake names
first_list = [
    "Alison",
    "Ashley",
    "Barbara",
    "Benjamin",
    "Bernice",
    "Betsy",
    "Bonnie",
    "Brandon",
    "Brian",
    "Brittany",
    "Candy",
    "Catherine",
    "Cheryl",
    "Christina",
    "Clara",
    "Clarence",
    "Cythia",
    "Diane",
    "Dianne",
    "Donna",
    "Edward",
    "Gary",
    "Gladys",
    "Gudrun",
    "Hazel",
    "Henry",
    "Hugo",
    "Jamie" "Jay",
    "Jill",
    "John",
    "Katherine",
    "Kellie",
    "Kelly",
    "Ken",
    "Leon",
    "Lillie",
    "Lori",
    "Luke",
    "Marion",
    "Michell",
    "Nicole",
    "Robert",
    "Robin",
    "Ruth",
    "Stanley",
    "Steven",
    "Thomas",
    "Toni",
]

last_list = [
    "Baylock",
    "Benites",
    "Blevins",
    "Bossert",
    "Bowen",
    "Campbell",
    "Cartwright",
    "Cayer",
    "Corradino",
    "Desrochers",
    "Doggett",
    "Drain",
    "Elizondo",
    "Enos",
    "Gardner",
    "Gill",
    "Hagadone",
    "Hernandez",
    "Hunt",
    "King",
    "Kirk",
    "Larose",
    "Licea",
    "Malone",
    "Martin",
    "Massaro",
    "Mcelvain",
    "Moore",
    "Paez",
    "Phang",
    "Randle",
    "Read",
    "Redding",
    "Rich",
    "Rioux",
    "Rivera",
    "Rodriguez",
    "Rollins",
    "Russell",
    "Sawyer",
    "Shaw",
    "Shortridge",
    "Spurbeck",
    "Stumpe",
    "Tiburcio",
    "Tran",
    "Vest",
    "Villa",
    "Waters",
    "Watts",
]

# list to create fake emails
email_list = [
    "gmail",
    "hotmail",
    "yahoo",
    "protonmail",
    "outlook",
    "aol",
    "zoho",
    "icloud",
    "gmx",
]


# random name
def random_name():
    """
    To create random names using common first and last names

    :returns: random first and last name
    """
    first = random.choice(first_list)
    last = random.choice(last_list)
    return (first, last)


def random_email(username):
    """
    To create fake email id using fake usernames for github

    :param username: fake username

    :returns: fake email
    """
    email = f"{username}@{random.choice(email_list)}.com"
    return email


def random_username(first, last):
    """
    To create fake usernames for github
    :param first: random first name
    :param last: random last name

    :returns: fake username
    """
    username = f"{first}_{last}{random.randint(0,100)}"
    return username


# lists to create fake data for assessments table
assessments_name = [
    "Back-End Web Development",
    "ChIP-Seq Analysis",
    "Linux for Bioinformatics",
    "Python Programming",
    "Python for Data Science",
    "R Programming",
    "R for Data Science",
    "RNA-Seq Analysis",
    "Single-Cell RNA-Seq Analysis",
    "Front-End Web Development",
]

assessment_desc = [
    "Creating a REST API backend using python and the flask framework.",
    "To analyze two ChIP-Seq datasets and compare the results.",
    "AWS EC2, SFTP, scripting, sudo, docker, Salmon, Quantify RNA-Seq Data",
    "Write a python script to play a game of Tic-Tac-Toe against your computer.",
    "Comprehensive analysis of the gapminder_clean.csv using jupyter notebook in .html format.",
    "R script that will allow you to play a game of Tic-Tac-Toe against computer",
    "Analyze the gapminder_clean.csv dataset using R and the tidyverse",
    "Find an RNA-Seq dataset and perform differential gene expression analysis.",
    "Complete a full scRNA-Seq analysis, including interpreting the results in a biological context.",
    "Creating a web application based on react.js.",
]

pre_requisite_id = [
    [3, 4, 5],
    [7],
    None,
    None,
    [4],
    None,
    [6],
    [6, 7],
    [6, 7, 8],
    None,
]
