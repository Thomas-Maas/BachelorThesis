import random

time = ["morning", "afternoon", "evening", "night"]
car_types = ["toyota", "honda", "ford", "chevrolet", "nissan", "bmw", "audi", "mercedes", "volkswagen", "hyundai", "renault", "peugeot", "fiat", "kia", "subaru", "mazda", "volvo", "mitsubishi", "land rover", "jaguar"]
car_colors = ["red", "blue", "green", "black", "white", "silver", "yellow", "orange", "purple", "brown", "pink", "gray", "gold", "teal", "cyan", "magenta", "maroon", "navy", "olive", "turquoise", "violet"]
bogus = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]


original_witness_names = [
    'abigail', 'alexandria', 'alexis', 'alicia', 'allison', 'alyssa', 'amanda', 'amber', 'amy', 'andrea',
    'angel', 'angela', 'anna', 'anne', 'annette', 'ariel', 'ashley', 'autumn', 'ava', 'barbara',
    'becca', 'bella', 'bernadette', 'beth', 'bianca', 'bonnie', 'brenda', 'briana', 'brianna', 'candice',
    'carmen', 'carol', 'caroline', 'cassandra', 'catherine', 'celeste', 'charlotte', 'cheryl', 'chloe', 'claire',
    'clara', 'colleen', 'crystal', 'cynthia', 'daisy', 'danielle', 'deborah', 'delia', 'destiny', 'diana',
    'diane', 'donna', 'elaine', 'elena', 'eliza', 'elizabeth', 'ella', 'ellen', 'emily', 'emma',
    'erica', 'eva', 'evelyn', 'faith', 'felicia', 'fiona', 'flora', 'frances', 'freya', 'gabrielle',
    'georgia', 'gina', 'grace', 'gwendolyn', 'hailey', 'hannah', 'harper', 'hazel', 'heather', 'heidi',
    'helena', 'holly', 'imogen', 'irene', 'isabel', 'isla', 'ivy', 'jacqueline', 'jade', 'jamie',
    'jane', 'jasmine', 'jean', 'jenna', 'jennifer', 'jessica', 'joan', 'jocelyn', 'jordan', 'joy',
    'judith', 'julia', 'julie', 'karen', 'kara', 'karen', 'kate', 'katherine', 'katie', 'kayla',
    'kelly', 'kelsey', 'kim', 'kristen', 'laura', 'lauren', 'leah', 'leslie', 'lily', 'linda',
    'lisa', 'lucy', 'luna', 'lydia', 'madeline', 'madison', 'maria', 'marie', 'marilyn', 'marina',
    'mary', 'megan', 'melanie', 'melissa', 'mia', 'michelle', 'mira', 'molly', 'mona', 'nancy',
    'naomi', 'natalie', 'nicole', 'nina', 'nora', 'olivia', 'opal', 'paige', 'pamela', 'patricia',
    'paula', 'penelope', 'penny', 'phoebe', 'rachel', 'rebecca', 'rita', 'robin', 'rosa', 'rosalie',
    'rose', 'ruby', 'sabrina', 'samantha', 'sandra', 'sara', 'sarah', 'savannah', 'serena', 'sharon',
    'sheila', 'sherri', 'sophia', 'stacy', 'stella', 'stephanie', 'susan', 'suzanne', 'sydney', 'tara',
    'taylor', 'teresa', 'theresa', 'tiffany', 'tina', 'tracy', 'una', 'ursula', 'valerie', 'vanessa',
    'vera', 'veronica', 'victoria', 'violet', 'wendy', 'whitney', 'willow', 'winona', 'xena', 'xiomara',
    'yara', 'yasmin', 'yvette', 'zoe', 'zora', 'zinnia'
]

temp_names = []
for x in original_witness_names:
    for y in original_witness_names:
        temp_names.append(x + y)
original_witness_names = temp_names.copy()





original_suspect_names = [
    'aaron', 'abel', 'adam', 'aiden', 'alan', 'albert', 'alec', 'alejandro', 'alex', 'alexander',
    'alfred', 'allen', 'andrew', 'anthony', 'arnold', 'arthur', 'austin', 'barry', 'ben', 'benjamin',
    'bernard', 'bill', 'billy', 'blake', 'bob', 'brad', 'bradley', 'brandon', 'brian', 'bruce',
    'caleb', 'cameron', 'carl', 'carter', 'charles', 'chris', 'christian', 'christopher', 'clark', 'clayton',
    'cliff', 'clint', 'colin', 'connor', 'craig', 'curtis', 'dan', 'daniel', 'danny', 'darren',
    'david', 'dean', 'dennis', 'derek', 'devin', 'dominic', 'doug', 'dylan', 'edgar', 'edward',
    'eli', 'elijah', 'elliot', 'emmett', 'eric', 'ethan', 'evan', 'felix', 'fernando', 'finn',
    'frank', 'fred', 'gabriel', 'gage', 'gabe', 'gavin', 'george', 'gerald', 'gilbert', 'glenn',
    'grant', 'greg', 'gregory', 'griffin', 'harold', 'harry', 'harvey', 'henry', 'howard', 'hunter',
    'ian', 'isaac', 'isaiah', 'ivan', 'jack', 'jacob', 'jake', 'james', 'jamie', 'jared',
    'jason', 'jay', 'jeff', 'jeffrey', 'jeremy', 'jerome', 'jerry', 'jesse', 'jim', 'jimmy',
    'joe', 'joel', 'john', 'johnny', 'jon', 'jonah', 'jonathan', 'jordan', 'jose', 'josh',
    'joshua', 'juan', 'julian', 'justin', 'karl', 'keith', 'ken', 'kenneth', 'kevin', 'kurt',
    'kyle', 'larry', 'lawrence', 'lee', 'leon', 'leo', 'leonard', 'liam', 'logan', 'louis',
    'lucas', 'luke', 'malcolm', 'marcus', 'mark', 'martin', 'mason', 'matt', 'matthew', 'michael',
    'miguel', 'mike', 'miles', 'nathan', 'neil', 'nick', 'noah', 'norman', 'omar', 'orion',
    'oscar', 'owen', 'paul', 'peter', 'philip', 'phillip', 'preston', 'quentin', 'quincy', 'randy',
    'ray', 'raymond', 'richard', 'riley', 'rob', 'robert', 'robin', 'roger', 'ron', 'ronald',
    'ross', 'roy', 'russell', 'ryan', 'sam', 'samuel', 'scott', 'sean', 'seth', 'shawn',
    'stanley', 'stephen', 'steve', 'steven', 'stuart', 'ted', 'terry', 'thomas', 'tim', 'timothy',
    'tom', 'tony', 'trent', 'tristan', 'troy', 'tyler', 'ulysses', 'umar', 'uri', 'vernon',
    'victor', 'vince', 'vincent', 'wade', 'walter', 'wayne', 'wesley', 'will', 'william', 'wyatt',
    'xander', 'xavier', 'yahir', 'yusuf', 'zack', 'zane', 'zion'
]

witness_names = original_witness_names.copy()
suspect_names = original_suspect_names.copy()
all_names_original = witness_names + suspect_names
all_names = all_names_original.copy()


def reset_names():
    """
    Resets the witness and suspect names to their original lists.
    """
    global witness_names, suspect_names, all_names
    witness_names = original_witness_names.copy()
    suspect_names = original_suspect_names.copy()
    all_names = (witness_names + suspect_names).copy()

def get_random_name_id():
    """
    Returns a random name and its ID from the combined list of witness and suspect names.
    """
    if len(all_names) == 0:
        raise ValueError("No more names available.")
    
    name = random.choice(all_names)
    all_names.remove(name)
    return len(all_names_original) - len(all_names), name

def get_available_witness_id_name():
    """
    Returns a list of available witness names.
    """
    if len(witness_names) == 0:
        raise ValueError("No more witness names available.")
    
    name = random.choice(witness_names)
    witness_names.remove(name)
    return len(original_witness_names) - len(witness_names), name

def get_available_suspect_id_name():
    """
    Returns a list of available suspect names.
    """
    if len(suspect_names) == 0:
        raise ValueError("No more suspect names available.")
    name = random.choice(suspect_names)
    suspect_names.remove(name)
    return len(original_suspect_names) - len(suspect_names), name


def get_random_time_of_day():
    """
    Returns a random time of day from the predefined list.
    """
    return random.choice(time)

def get_random_car_type():
    """
    Returns a random car type from the predefined list.
    """
    return random.choice(car_types)

def get_random_car_color():
    """
    Returns a random car color from the predefined list.
    """
    return random.choice(car_colors)

def get_random_witness_name():
    """
    Returns a random witness name from the predefined list.
    """
    return random.choice(witness_names)

def get_random_suspect_name():
    """
    Returns a random suspect name from the predefined list.
    """
    return random.choice(suspect_names)
def get_random_bogus():
    """
    Returns a random bogus value from the predefined list.
    """
    return random.choice(bogus)

print(len(witness_names), len(suspect_names))