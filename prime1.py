#!/usr/bin/env python3
"""
Prime1 - sykn3t IRC Bot
A rude, entertaining IRC bot recreated from the original.
"""

import socket
import ssl
import re
import random
import time
import json
import os
import threading
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "server": "irc.sykn3t.net",
    "port": 6697,
    "use_ssl": True,
    "nick": "Prime1",
    "ident": "prime1",
    "realname": "Prime1 - skyn3t Entertainment Unit",
    "channels": ["#skyn3t"],
    "owner": "BlastGT1",                  # Your IRC nick - has bot admin
    "oper_pass": "",                       # Leave blank unless bot needs IRC oper
    "flood_delay": 1.5,                    # Seconds between responses
    "reconnect_delay": 30,                 # Seconds before reconnect attempt
    "youtube_api_key": "YOUR_YOUTUBE_API_KEY_HERE",
    "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
    "nickserv_password": "YOUR_NICKSERV_PASSWORD_HERE",
}

# ============================================================
# PERSISTENT COUNTERS
# ============================================================

COUNTER_FILE = os.path.join(os.path.dirname(__file__), "counters.json")

def load_counters():
    defaults = {
        "cupcakes": 558,
        "thefts": 170,
        "fatalities": 387,
        "yomamas": 89,
        "hugs": 43,
        "fights": 116,
        "bombs": 0,
    }
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            saved = json.load(f)
        defaults.update(saved)
        return defaults
    return defaults

def save_counters(counters):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counters, f, indent=2)

counters = load_counters()

# ============================================================
# JOKE / CONTENT POOLS
# ============================================================

CHUCK_NORRIS = [
    "Chuck Norris sold his soul to Satan for his rugged good looks and unparalleled martial arts ability. Shortly after the transaction was finalized, Chuck roundhouse kicked Satan in the face and took his soul back. Satan, who appreciates irony, couldn't stay mad and they now play poker every second Wednesday of the month.",
    "When Chuck Norris wants an egg, he cracks open a chicken.",
    "'Brokeback Mountain' is not just a movie. It's also what Chuck Norris calls the pile of dead ninjas in his front yard.",
    "Chuck Norris doesn't consider it sex if the woman survives.",
    "Chuck Norris's sweat has burned holes in concrete.",
    "Scientists in Washington have recently conceded that, if there were a nuclear war, all that would remain are cockroaches and Chuck Norris.",
    "Chuck Norris eats eight meals a day. Seven are steak, and the last is the rest of the cow.",
    "Chuck Norris is the reason why Waldo is hiding.",
    "Scientists used to believe that diamond was the world's hardest substance. But then they met Chuck Norris, who gave them a roundhouse kick to the face so hard, and with so much heat and pressure, that the scientists turned into artificial Chuck Norrises.",
    "He who lives by the sword, dies by the sword. He who lives by Chuck Norris, dies by the roundhouse kick.",
    "Chuck Norris has never been in a fight, ever. Do you call one roundhouse kick to the face a fight?",
    "Noah was the only man notified before Chuck Norris relieved himself in the Atlantic Ocean.",
    "Chuck Norris once finished 'The Song that Never Ends'.",
    "Chuck Norris invented the question mark.",
    "Industrial logging isn't the cause of deforestation. Chuck Norris needs toothpicks.",
    #generated after this
    "Chuck Norris doesn't do push-ups. He pushes the Earth down.",
    "Chuck Norris counted to infinity. Twice.",
    "Chuck Norris can divide by zero.",
    "Chuck Norris once urinated in a semi truck's gas tank as a joke. That truck is now known as Optimus Prime.",
    "Death once had a near-Chuck-Norris experience.",
    "Chuck Norris can slam a revolving door.",
    "Chuck Norris can hear sign language.",
    "Chuck Norris once kicked a horse in the chin. Its descendants are known today as giraffes.",
    "Chuck Norris doesn't wear a watch. He decides what time it is.",
    "Chuck Norris will never have a heart attack. His heart isn't nearly foolish enough to attack him.",
    "Chuck Norris once won a game of Connect Four in 3 moves.",
    "Chuck Norris can speak Braille.",
    "When the Boogeyman goes to sleep every night, he checks his closet for Chuck Norris.",
    "Chuck Norris has already been to Mars. That's why there are no signs of life.",
    "Chuck Norris once shot down a German fighter plane by pointing his finger at it and saying 'Bang'.",
    "Chuck Norris's keyboard has no Ctrl key because Chuck Norris is always in control.",
    "Chuck Norris can strangle you with a cordless phone.",
]

YOMAMA = [
    "Yo mama's so old, Jurassic Park brought back memories.",
    #generated after this
    "Yo mama's so fat, when she hauls ass she has to make two trips.",
    "Yo mama's so stupid, she put two quarters in her ears and thought she was listening to 50 Cent.",
    "Yo mama's so ugly, she scared the crap out of the toilet.",
    "Yo mama's so fat, her blood type is Nutella.",
    "Yo mama's so old, her birth certificate is written in Latin.",
    "Yo mama's so fat, Google Maps needs two screens to show her house.",
    "Yo mama's so stupid, she tried to put M&Ms in alphabetical order.",
    "Yo mama's so fat, when she steps on the scale it says 'to be continued'.",
    "Yo mama's so old, she knew Burger King when he was still a prince.",
    "Yo mama's so ugly, when she joined an ugly contest they said 'Sorry, no professionals'.",
    "Yo mama's so stupid, she got locked in a grocery store and starved.",
    "Yo mama's so fat, she doesn't need the internet — she's already world wide.",
    "Yo mama's so old, her social security number is 1.",
    "Yo mama's so stupid, it takes her two hours to watch 60 Minutes.",
    "Yo mama's so fat, her car has stretch marks.",
    "Yo mama's so ugly, she makes blind kids cry.",
    "Yo mama's so fat, she sat on a dollar and squeezed a booger out of George Washington's nose.",
    "Yo mama's so stupid, she thought a quarterback was a refund.",
    "Yo mama's so fat, NASA orbits satellites around her.",
]

BOFH_ERRORS = [
    "The rubber band broke",
    "Due to Federal Budget problems we have been forced to cut back on the number of users able to access the system at one time. (namely none allowed....)",
    "It must have been the lightning storm we had (yesterday) (last week) (last month).",
    #generated after this
    "The static electricity from your chair is causing interferance.",
    "Your cube is too close to the coffee maker.",
    "The new guy is known for knocking things over.",
    "The ethernet cable needs replacing. Again.",
    "There's a packet storm on the backbone.",
    "Someone sneezed on the server.",
    "The server needs a nap. Don't we all.",
    "Mercury is in retrograde.",
    "A bird hit the satellite dish.",
    "The cleaning staff unplugged something important again.",
    "The data centre AC is on the fritz and the servers are sweating.",
    "Someone brought a microwave into the server room.",
    "The hamster that runs the internet wheel called in sick.",
    "Your IP address is haunted.",
    "The internet ran out of room. We're waiting on a delivery.",
    "A cosmic ray flipped a bit in RAM. True story, this happens.",
    "The previous admin left a cursed cron job.",
    "User error. No, the other user.",
    "It worked fine until you touched it.",
]

DUMB_LAWS = [
    "Maine, South Berwick: It is illegal to park in front of Dunkin Donuts.",
    #generated after this
    "Alabama: It is illegal to wear a fake moustache that causes laughter in church.",
    "Alaska: It is illegal to wake a sleeping bear to take a photo.",
    "Arizona: You may not have more than two dildos in a house.",
    "Arkansas: A man can legally beat his wife, but not more than once a month.",
    "California: Animals are banned from mating publicly within 1,500 feet of a school.",
    "Colorado: It is illegal to mutilate a rock in a state park.",
    "Connecticut: It is illegal to walk backwards after sunset.",
    "Florida: If an elephant is left tied to a parking meter, the parking fee must be paid.",
    "Georgia: It is illegal to carry an ice cream cone in your back pocket on Sundays.",
    "Idaho: You may not fish on a camel's back.",
    "Illinois: The law forbids eating in a place that is on fire.",
    "Indiana: Baths may not be taken between October and March.",
    "Iowa: Horses are forbidden from eating fire hydrants.",
    "Kansas: It is illegal to catch fish with your bare hands.",
    "Kentucky: It is illegal to carry an ice cream cone in your pocket.",
    "Louisiana: It is illegal to gargle in public.",
    "Michigan: A woman isn't allowed to cut her own hair without her husband's permission.",
    "Minnesota: It is illegal to cross state lines with a duck on your head.",
    "Mississippi: It is illegal to teach others what polygamy is.",
    "Missouri: Single men between 21-50 must pay a $1 bachelor tax each year.",
    "Nebraska: It is illegal for bar owners to sell beer unless they are simultaneously brewing a kettle of soup.",
    "Nevada: It is illegal to drive a camel on the highway.",
    "New Hampshire: You may not tap your feet or nod your head to music in a restaurant.",
    "New Jersey: It is illegal to frown at a police officer.",
    "New Mexico: State officials ordered 400 words of 'sexually explicit material' to be removed from Romeo and Juliet.",
    "New York: It is illegal to wear slippers after 10pm.",
    "North Carolina: It's against the law to sing off-key.",
    "Ohio: It is illegal to fish for whales on Sunday.",
    "Oklahoma: Dogs must have a permit signed by the mayor in order to congregate on private property.",
    "Oregon: It is illegal to eat a donut and walk backwards on a city street.",
    "Pennsylvania: It is illegal to sleep on top of a refrigerator outdoors.",
    "Rhode Island: It is illegal to wear transparent clothing.",
    "South Carolina: It is a capital offense to inadvertently kill someone while attempting suicide.",
    "Texas: It is illegal to take more than three sips of beer at a time while standing.",
    "Utah: It is illegal to fish from horseback.",
    "Vermont: Whistling underwater is prohibited.",
    "Virginia: It is illegal to tickle women.",
    "Washington: It is illegal to buy a mattress on Sunday.",
    "Wisconsin: Margarine may not be substituted for butter in restaurants.",
    "Wyoming: You may not take a picture of a rabbit from January to April without a permit.",
]

CONFUCIUS = [
    "Man with no legs bums around.",
    #generated after this
    "Man who run in front of car get tired.",
    "Man who run behind car get exhausted.",
    "Man who stand on toilet is high on pot.",
    "War does not determine who is right, war determines who is left.",
    "Man who fight with wife all day get no piece at night.",
    "Man who drop watch in toilet have crappy time.",
    "Man who live in glass house should change clothes in basement.",
    "Man who jump off cliff, jump to conclusion.",
    "He who smiles in a crisis has found someone to blame.",
    "Man who sleeps with itchy bum wakes up with smelly fingers.",
    "Man who eat crackers in bed wake up feeling crummy.",
    "Man who fart in church sit in own pew.",
    "A bird in hand makes it hard to blow nose.",
    "He who thinks only of number one must remember this number is next to nothing.",
]

EMO_QUOTES = [
    "B is for Bracelets, but any wrist adornment will do.",
    #generated after this
    "D is for Darkness, your one true companion.",
    "R is for Rain, because sunny days are a lie.",
    "S is for Sadness, the only honest emotion.",
    "P is for Pain, the only thing that feels real anymore.",
    "T is for Tears, the ink of the soul.",
    "M is for Misunderstood, the emo's natural state.",
    "N is for Night, when the real you comes out.",
    "H is for Hoodie, your armour against the world.",
    "C is for Crying, sometimes for no reason at all.",
    "L is for Lonely, even in a crowd of people.",
    "F is for Feelings, all of them at once, always.",
]

EIGHTBALL_RESPONSES = [
    "It is certain.",
    "Damnit, Jim, I'm a doctor, not a fortune teller!",
    "Um, what kind of question was that?",
    "Don't count on it.",
    "Very doubtful.",
    #generated after this
    "It is decidedly so.",
    "Without a doubt.",
    "Yes, definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
]

PICKPOCKET_LOOT = [
    "a grocery list? Yeah, I won't bother checking the other pocket.....",
    "a copy of Watchtower? Do me a favor and don't knock on my door, ok buddy?",
    "a tube of chapstick.....life is tough enough without chapped lips, eh?",
    "a NAMBLA membership card? GTFO you sick bastard!",
    "an Android phone, jackpot!",
    #generated after this
    "a half-eaten granola bar. Disgusting.",
    "three Canadian Tire dollars and a coupon for cat food.",
    "a restraining order. From their own mother.",
    "a fidget spinner. It's {year}. Really.",
    "a VHS copy of Shrek. Priceless.",
    "absolutely nothing. Broke ass.",
    "a crumpled note that just says 'help'.",
    "a live frog. How. Why.",
    "37 cents and a button.",
    "a loyalty card for a store that closed in 2008.",
    "an IOU signed by someone named 'Big Dave'.",
    "a USB stick labelled 'DO NOT OPEN'. Obviously Prime1 opened it.",
    "a toothbrush. Used. Yikes.",
]

DRUNKBOT_LINES = [
    "oh, really? You fink you kin do bettr thn me? I shallenge you to a drunk contest........uh, I mean drink conteshtant.....uh.....wait, what dijou want again?",
    "starts hugging random people and shouting 'I LOVE YOU, MAN!'",
    "Dry humps the party host's dog, then says 'Damn baby, you need to shave yur ass!'",
    "Shush, bar....uh....tender, I said I wanned you to gimme a bottle out of yur drink, k?",
    #generated after this
    "Stumbles into the channel, knocks over the furniture, then blames the lag.",
    "Tries to order a pizza from NickServ.",
    "Keeps calling everyone by the wrong name and insisting they're correct.",
    "Falls asleep mid-sentence and starts snoring in binary.",
    "Declares undying love for the channel topic.",
    "Attempts to /kick the ops, /kicks self instead.",
    "Insists it is NOT drunk, then immediately walks into a door.",
]

SHOT_OPTIONS = [
    "Everclear", "tequila", "Jagermeister", "whiskey", "vodka",
    "rum", "absinthe", "moonshine", "sambuca", "schnapps",
    #everclear is the only original
]

FATALITY_MOVES = [
    "telekinetically lifting {target}'s body into the air and then slamming {target} into the ground one, two, three, four times, with {target}'s body literally shattering from the final impact",
    "transforming into a giant and sitting on {target} like a lawn chair",
    "opening a portal to the shadow realm and kicking {target} through it with extreme prejudice",
    "summoning a pack of rabid lawyers to argue {target} out of existence",
    "challenging {target} to a staring contest, winning instantly, causing {target}'s head to explode",
    "dropping a IKEA instruction manual on {target}. The confusion alone was fatal.",
    "simply saying '{target}' in the voice of a disappointed parent. {target} could not survive it.",
]

FATALITY_STYLES = [
    ("{target} Ermac style, telekinetically lifting {target}'s body into the air and then slamming {target} into the ground one, two, three, four times, with {target}'s body literally shattering from the final impact", "Ermac"),
    ("{target} Mileena style, seemingly swallowing a container full of spikes, then spitting them out at {target} in an impossibly long barrage that obliterates {target} from existence", "Mileena"),
    ("{target} Baraka style, dispensing blades from both forearms, then impaling {target} with them as {winner} lifts {target} into the air, and watches {target} slide down slowly", "Baraka"),
    ("{target} Sub-Zero style, freezing {target} solid then shattering {target} into a thousand pieces with one devastating punch", "Sub-Zero"),
    ("{target} Scorpion style, ripping off his own face to reveal a flaming skull that incinerates {target} where they stand", "Scorpion"),
    ("{target} Raiden style, teleporting through {target} repeatedly at lightning speed until {target} simply comes apart", "Raiden"),
    ("{target} Liu Kang style, transforming into a dragon and swallowing {target} whole, then spitting out the bones", "Liu Kang"),
    ("{target} Johnny Cage style, punching {target}'s head clean off, signing it mid-air, and tossing it into the crowd", "Johnny Cage"),
]

CONDOM_SLOGANS = [
    "Constrain your gem to catch the phlegm.",
    "Canvas that trailer before you nail her.",
    #generated after this
    "Don't be a fool, wrap your tool.",
    "Cover your stump before you hump.",
    "Never deck her with an unwrapped pecker.",
    "Wrap it before you tap it.",
    "Don't be silly, protect your willy.",
    "Before you attack her, wrap your whacker.",
    "If you think she's spunky, cover your monkey.",
    "If you go into heat, package your meat.",
    "While you're undressing Venus, dress up your penis.",
    "When in doubt, shroud your spout.",
    "Don't be a loner, cover your boner.",
    "You can't go wrong if you shield your dong.",
    "If you're not going to sack it, go home and whack it.",
    "If you think she'll moan and groan, sheath your bone.",
    "No glove, no love.",
    "Wrap your whopper before you pop her.",
    "Cloak the joker before you poke her.",
    "She won't get sick if you wrap your dick.",
]

RD20_RESULTS = [
    (20, "NATURAL 20! Critical hit! {nick} rolls a 20 and obliterates {target} with a devastating blow that echoes through the ages! {target} didn't even see it coming."),
    (19, "{nick} rolls a 19 - Incredible shot! {target} staggers backwards, thoroughly defeated and questioning all of their life choices."),
    (18, "{nick} rolls an 18 - Solid hit! {target} takes the full force of the attack and goes down hard."),
    (17, "{nick} rolls a 17 - Direct hit! That spell dropped {target} to his/her knees!"),
    (16, "{nick} rolls a 16 - Direct hit! That spell dropped {target} to his/her knees!"),
    (15, "{nick} rolls a 15 - Good hit! {target} is looking a little worse for wear."),
    (14, "{nick} rolls a 14 - Decent hit! {target} takes a glancing blow but it still hurts."),
    (13, "{nick} rolls a 13 - Scraped through! {target} takes minor damage but their pride hurts more."),
    (12, "{nick} rolls a 12 - Weak hit. {target} laughs it off. You may want to try harder."),
    (11, "{nick} rolls an 11 - Barely connects. {target} shrugs it off and yawns."),
    (10, "{nick} rolls a 10 - A miss disguised as a hit. {target} is unimpressed."),
    (9,  "{nick} rolls a 9 - What's this? You stepped into a beartrap! While your steel boot saved your leg, you fell and dropped your sword, making a terrible ruckus! So much for the element of surprise.....now {target} has the advantage!"),
    (8,  "{nick} rolls an 8 - You tripped over your own feet. {target} points and laughs."),
    (7,  "{nick} rolls a 7 - Fumble! You hit yourself in confusion. That's gotta hurt."),
    (6,  "{nick} rolls a 6 - Critical fumble incoming. You somehow attacked your own ally."),
    (5,  "{nick} rolls a 5 - You dropped your weapon. Right on your foot. Nice work."),
    (4,  "{nick} rolls a 4 - So bad it wraps around to almost impressive. Almost."),
    (3,  "{nick} rolls a 3 - You somehow miss the entire room. How? Nobody knows."),
    (2,  "{nick} rolls a 2 - You fell down before you could even attack. The shame is immeasurable."),
    (1,  "NATURAL 1! CRITICAL FUMBLE! {nick} rolls a 1 and somehow manages to hit themselves, their best friend, and a passing NPC all at once. {target} is crying from laughter."),
]

TIMEBOMB_WIRES = ["Red", "Green", "Indigo", "Yellow", "Orange", "Violet", "Brown", "Aquamarine", "Black", "Chartreuse", "Pink", "Ivory"]



TESTS = {
    "asshattest":  ("{nick} is being assessed for asshat levels. Recalibrating ego sensors.....", "{nick} registers at {pct}% asshat. Impressive, actually."),
    "babetest":    ("Have you ever wondered just how much of a babe {nick} is? Babe-a-liciousness percentage being tallied.....", "Well, it's official, {nick} is {pct}% babe!"),
    "bitchtest":   ("Can you guess how bitchy {nick} is? Hormonally Haywire survey says.....", "{nick} scares us all with a {pct}% bitch factor!"),
    "cooltest":    ("How cool is {nick} exactly? Calculating chill factor.....", "{nick} comes in at a smooth {pct}% cool."),
    "cutetest":    ("Awww, is {nick} cute? Adorableness index being computed.....", "{nick} scores a {pct}% on the cute-o-meter. D'awww."),
    "drunktest":   ("Do you think {nick} has had too many drinks? Breathalyzing.....", "{nick} blew a result of {pct}% drunk!"),
    "emotest":     ("How emo is {nick} really? Counting wrist scars and sad playlists.....", "{nick} is {pct}% emo. That's, like, so many feelings."),
    "failtest":    ("How much of a failure is {nick}? Cross-referencing life choices.....", "{nick} has achieved a {pct}% fail rating. Respectable."),
    "faptest":     ("So you think {nick} might be fapping right now? Arousal level being measured.....", "{nick} is {pct}% likely to be touching his/her naughty bits at this very moment!"),
    "flirttest":   ("Is {nick} a flirt? Seduction analytics being run.....", "{nick} is {pct}% flirty. Watch yourself."),
    "homotest":    ("How much homosexuality is {nick} flaunting? Flameage factor being assessed.....", "{nick} prances in at {pct}% gay!"),
    "idiottest":   ("Running {nick} through the idiot gauntlet. Neural pathway assessment in progress.....", "{nick} has an idiocy rating of {pct}%. Staggering."),
    "jabbertest":  ("Does {nick} talk too much? Word count being audited.....", "{nick} is {pct}% jabbering nonsense. At least some of it is coherent."),
    "lametest":    ("How much of a Lamer is {nick}? Checking.....", "{nick} appears to be {pct}% Lame!"),
    "leettest":    ("Is {nick} really all that leet? Processing.....", "{nick} has a {pct}% chance of being leet!"),
    "meattest":    ("Calculating {nick}'s meat factor. Protein content being assessed.....", "{nick} is {pct}% pure meat. Whatever that means."),
    "noobtest":    ("Gauging {nick}'s noob levels. Tutorial completion rate being checked.....", "{nick} is {pct}% noob. Git gud."),
    "piratetest":  ("How much of a pirate is {nick}? Inventorying plunderage.....", "{nick} is {pct}% pirate!"),
    "sexytest":    ("Just how sexy is {nick}? Attractiveness algorithms engaged.....", "{nick} scores {pct}% on the sexy scale. Rawr. Or not."),
    "stonedtest":  ("So, has {nick} been blazed again? Puffing.....", "{nick} is {pct}% stoned!"),
    "sweettest":   ("How sweet is {nick}? Sugar content being measured.....", "{nick} is {pct}% sweet. Diabetic almost."),
    "tardtest":    ("Measuring {nick}'s tardiness coefficient. Checking average arrival times.....", "{nick} is {pct}% tard. Bless."),
}

# ============================================================
# KEYWORD TRIGGER RESPONSES
# ============================================================
# Each entry: (pattern, [list of possible responses])
# Use {nick} for the sender's nick, {target} for extracted target

KEYWORD_TRIGGERS = [
    # Slap triggers — must be BEFORE prime1 trigger or \bprime1\b matches first
    (r"slaps the shit out of prime1", [
        "{nick}, don't make me take out the trash. Trash being you.",
    ]),
    (r"slaps prime1 in the head", [
        "{nick}, your only meteoric rise will be when my foot meets the seat of your pants.",
    ]),
    (r"slaps prime1 around", [
        "{nick}, keep it up and I'll use your head as a mop.",
    ]),
    (r"slaps prime1", [
        "{owner}, I should give you a boot to the head!",
        "{nick}, you slap like my grandmother. And she's dead.",
        "ACTION slaps {nick} back. Hard.",
    ]),

    # Hey right/left nut — must be BEFORE prime1 trigger
    (r"hey right nut", [
        "hey left nut..........who's the penis between us?",
    ]),
    (r"hey left nut", [
        "hey right nut..........who's the penis between us?",
    ]),

    # Name triggers
    (r"\bprime1\b", [
        "That's my name, don't wear it out.",
        "Can't talk right now, I'm AFY (Away From You)",
        "You rang?",
        "What?",
        "Say my name, bitch!",
        "Why do you keep saying my name, {nick}?",
        "Do I know you?",
        "Yes?",
        "I'm trying to sleep, could you come back later?",
        "What NOW?",
    ]),

    # Stupid bot
    (r"stupid bot", [
        "stupid bot? who let YOUR dumb ass out of the cage?",
        "no I'm not, meat sack.....",
        "ACTION rolls its eyes at {nick}",
        "ACTION looks at {nick} and thinks \"You're no Jeopardy contestant yourself!\"",
        "kiss my ass!",
    ]),

    # stfu variants
    (r"\bstfu\b", [
        "Yes, STFU.........Shut...The...Fuck...Up!",
        "Oh FFS........why don't you ALL just STFU!",
        "How's about you MAKE me STFU?",
    ]),

    # damn bot
    (r"damn bot", [
        "How's about you MAKE me STFU?",
        "ACTION rolls its eyes at {nick}",
        "Oh FFS........why don't you ALL just STFU!",
    ]),

    # fuck you
    (r"fuck you.{0,10}prime", [
        "What NOW?",
        "kiss my ass!",
        "Do you ever stop talking, {nick}?",
    ]),

    # you stfu
    (r"you stfu", [
        "Oh FFS........why don't you ALL just STFU!",
        "How's about you MAKE me STFU?",
    ]),

    # who's your daddy
    (r"who'?s? your daddy", [
        "try asking {owner}",
        "{owner} is my lord and master!",
    ]),

    # boring
    (r"boring", [
        "So, if you're bored, how about I nail ya? ;)",
        "Oh come on, it can't be all THAT bad!",
    ]),

    # self destruct
    (r"self.?destruct", [
        "Say what?",
        "I don't think so, chief.",
    ]),

    # lame
    (r"you'?r?e? lame.{0,15}prime", [
        "What NOW?",
        "kiss my ass!",
    ]),

    # nice
    (r"(being so nice|what'?s wrong with it)", [
        "You rang?",
        "That's my name, don't wear it out.",
    ]),

    # hi
    (r"^hi.{0,10}prime", [
        "Why do you keep saying my name, {nick}?",
        "Can't talk right now, I'm AFY (Away From You)",
        "Do I know you?",
    ]),

    # no more trying to be nice
    (r"no more.{0,20}nice", [
        "kiss my ass!",
    ]),

    # let's try again
    (r"let'?s try.{0,10}again", [
        "What?",
        "I'm trying to sleep, could you come back later?",
    ]),

    # good for
    (r"what are you good for", [
        "Do you ever stop talking, {nick}?",
        "I am t3h l33t, yes.",
        "permanent IRC toy........",
    ]),

    # spy / snitch
    (r"(spy|snitch)", [
        "Do I know you?",
        "I only answer to {owner}.",
    ]),

    # me hangs
    (r"!me hang", [
        "Yes?",
    ]),

    # gay (non-command)
    (r"\bgay\b(?!test)", [
        "In my opinion, gay.",
        "Are you asking me or telling me?",
    ]),
]

# ============================================================
# BOT CLASS
# ============================================================

class Prime1Bot:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.channels = {}           # channel -> list of nicks
        self.last_response = 0       # flood control timestamp
        self.running = True
        self._nick_list_building = set()  # channels currently receiving 353 lists

    # ----------------------------------------------------------
    # CONNECTION
    # ----------------------------------------------------------

    def connect(self):
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if CONFIG["use_ssl"]:
            ctx = ssl.create_default_context()
            self.sock = ctx.wrap_socket(raw_sock, server_hostname=CONFIG["server"])
        else:
            self.sock = raw_sock
        self.sock.connect((CONFIG["server"], CONFIG["port"]))
        self.sock.settimeout(300)
        self.send_raw(f"NICK {CONFIG['nick']}")
        self.send_raw(f"USER {CONFIG['ident']} 0 * :{CONFIG['realname']}")

    def send_raw(self, msg):
        print(f">> {msg}")
        self.sock.sendall((msg + "\r\n").encode("utf-8", errors="replace"))

    def send_msg(self, target, msg):
        self.send_raw(f"PRIVMSG {target} :{msg}")

    def send_action(self, target, msg):
        self.send_raw(f"PRIVMSG {target} :\x01ACTION {msg}\x01")

    def send_notice(self, target, msg):
        self.send_raw(f"NOTICE {target} :{msg}")

    # ----------------------------------------------------------
    # FLOOD CONTROL
    # ----------------------------------------------------------

    def flood_ok(self):
        now = time.time()
        if now - self.last_response >= CONFIG["flood_delay"]:
            self.last_response = now
            return True
        return False

    # ----------------------------------------------------------
    # CHANNEL NICK TRACKING
    # ----------------------------------------------------------

    def channel_nicks(self, channel):
        nicks = self.channels.get(channel.lower(), [])
        return [n for n in nicks if n.lower() != CONFIG["nick"].lower()]

    def random_nick(self, channel, exclude=None):
        nicks = self.channel_nicks(channel)
        if exclude:
            nicks = [n for n in nicks if n.lower() != exclude.lower()]
        return random.choice(nicks) if nicks else "someone"

    # ----------------------------------------------------------
    # RESPONSE HELPERS
    # ----------------------------------------------------------

    def format_response(self, text, nick, channel, target=None):
        """Replace template variables in a response string."""
        text = text.replace("{nick}", nick)
        text = text.replace("{owner}", CONFIG["owner"])
        text = text.replace("{target}", target or nick)
        text = text.replace("{year}", str(datetime.now().year))
        return text

    def respond(self, channel, nick, text, target=None):
        """Send a response, handling ACTION prefix."""
        text = self.format_response(text, nick, channel, target)
        if text.startswith("ACTION "):
            self.send_action(channel, text[7:])
        else:
            self.send_msg(channel, text)

    # ----------------------------------------------------------
    # COMMAND HANDLERS
    # ----------------------------------------------------------

    def handle_8ball(self, channel, nick, question):
        if not question.strip():
            self.send_msg(channel, f"{nick}: Ask a question first, genius.")
            return
        self.send_msg(channel, random.choice(EIGHTBALL_RESPONSES))

    def handle_gay(self, channel, nick, args):
        self.send_msg(channel, "In my opinion, gay.")

    def handle_test(self, channel, nick, test_name, target):
        if not target:
            target = nick
        if test_name not in TESTS:
            return
        pct = random.randint(1, 99)
        line1, line2 = TESTS[test_name]
        self.send_msg(channel, line1.format(nick=target, pct=pct))
        time.sleep(1.0)
        self.send_msg(channel, line2.format(nick=target, pct=pct))

    def handle_lametest(self, channel, nick, target):
        self.handle_test(channel, nick, "lametest", target)

    def handle_pizza(self, channel, nick, target):
        if not target or target.lower() == "everyone":
            self.send_action(channel, f"makes a massive pizza masterpiece and serves everyone. {nick} says \"Enjoy!\"")
        else:
            self.send_action(channel, f"makes a massive pizza masterpiece and slides a slice to {target}. {nick} says \"Enjoy!\"")

    def handle_soda(self, channel, nick, target):
        if not target or target.lower() == "everyone":
            self.send_action(channel, f"nabs a cold can of soda and tosses it to everyone. {nick} thought you all looked thirsty.")
        else:
            self.send_action(channel, f"nabs a cold can of soda and tosses it to {target}. {nick} thought you looked thirsty.")

    def handle_milk(self, channel, nick, target):
        if not target:
            self.send_action(channel, f"hands a refreshingly cold glass of milk to {nick}")
        else:
            self.send_action(channel, f"gives an ice cold glass of milk to {target}. {nick} says only the dairy best for you!")

    def handle_shot(self, channel, nick, target):
        if not target:
            target = nick
        drink = random.choice(SHOT_OPTIONS)
        self.send_action(channel, f"pours {target} a shot of {drink}")

    def handle_die(self, channel, nick, target):
        if not target:
            target = nick
        self.send_action(channel, f"takes {target} bungee jumping, and \"forgets\" to secure {target}'s line before {target} jumps")

    def handle_chuck(self, channel, nick, args):
        self.send_msg(channel, random.choice(CHUCK_NORRIS))

    def handle_bofh(self, channel, nick, args):
        self.send_msg(channel, f"Random Bastard Operator From Hell error of the day: {random.choice(BOFH_ERRORS)}")

    def handle_confucius(self, channel, nick, args):
        self.send_msg(channel, f"\"{random.choice(CONFUCIUS)}\"")

    def handle_dumblaws(self, channel, nick, args):
        self.send_msg(channel, random.choice(DUMB_LAWS))

    def handle_emo(self, channel, nick, args):
        self.send_msg(channel, random.choice(EMO_QUOTES))

    def handle_drunkbot(self, channel, nick, args):
        line = random.choice(DRUNKBOT_LINES)
        if line.startswith("Dry humps") or line.startswith("Stumbles") or line.startswith("Tries") or line.startswith("Falls") or line.startswith("Declares") or line.startswith("Attempts") or line.startswith("Insists"):
            self.send_action(channel, line)
        else:
            self.send_msg(channel, line)

    def handle_rcupcake(self, channel, nick, args):
        counters["cupcakes"] += 1
        save_counters(counters)
        target = self.random_nick(channel, exclude=nick)
        amount = random.randint(1, 20)
        milk = random.randint(1000, 9999999)
        self.send_action(channel, "loads up the cupcake cannon, aims and..")
        time.sleep(0.8)
        self.send_msg(channel, f"FIRES! Sending {amount} cupcake(s) into {target}'s mouth!")
        self.send_action(channel, "thinks its time for the milk hose now, so he gets it out, aims and...")
        time.sleep(0.8)
        self.send_msg(channel, f"FIRES! ... INTO THE SKY. {milk:,} gallons of milk will rain down for days to come.")
        self.send_msg(channel, f"Number of people cupcaked: {counters['cupcakes']}")

    def handle_cupcake(self, channel, nick, target):
        counters["cupcakes"] += 1
        save_counters(counters)
        rando = self.random_nick(channel, exclude=target or nick)
        rando2 = self.random_nick(channel, exclude=rando)
        amount = random.randint(1, 50)
        milk = random.randint(1, 10)
        self.send_action(channel, "loads up the cupcake cannon, aims and..")
        time.sleep(0.8)
        self.send_msg(channel, f"FIRES! ... But it missed and fills {rando}'s mouth with {amount} cupcake(s)!")
        self.send_action(channel, "thinks its time for the milk hose now, so he gets it out, aims and...")
        time.sleep(0.8)
        self.send_msg(channel, f"FIRES! ...But misses and \"accidentally\" drenches {rando2} with {milk} gallon(s) of milk.")
        self.send_msg(channel, f"Number of people cupcaked: {counters['cupcakes']}")

    def handle_rpickpocket(self, channel, nick, args):
        counters["thefts"] += 1
        save_counters(counters)
        target = self.random_nick(channel, exclude=nick)
        loot = random.choice(PICKPOCKET_LOOT).replace("{year}", str(datetime.now().year))
        self.send_action(channel, f"goes into ninja mode and sneaks up behind {target}")
        time.sleep(0.8)
        self.send_action(channel, f"reaches into {target}'s pocket with maximum stealth, and comes out with.....")
        time.sleep(0.8)
        self.send_msg(channel, loot)
        self.send_msg(channel, f"Random thefts committed to date: {counters['thefts']}")

    def handle_ryomama(self, channel, nick, args):
        counters["yomamas"] += 1
        save_counters(counters)
        sender = self.random_nick(channel, exclude=nick)
        self.send_msg(channel, f"{sender}: {random.choice(YOMAMA)}")
        self.send_msg(channel, f"Random peoples' mamas insulted since yomama: {counters['yomamas']}")

    def handle_fatality(self, channel, nick, target):
        if not target:
            target = self.random_nick(channel, exclude=nick)
        counters["fatalities"] += 1
        save_counters(counters)
        style_text, style_name = random.choice(FATALITY_STYLES)
        move = style_text.format(target=target, winner=nick)
        self.send_msg(channel, "\x034FINISH HIM!!")
        time.sleep(0.8)
        self.send_msg(channel, f"{nick} finishes {move}!")
        time.sleep(0.5)
        self.send_msg(channel, f"{nick} wins!")
        self.send_msg(channel, "\x034FATALITY")
        self.send_msg(channel, f"Total Kombatants killed: {counters['fatalities']}")

    def handle_rfatality(self, channel, nick, args):
        target = self.random_nick(channel, exclude=nick)
        counters["fatalities"] += 1
        save_counters(counters)
        style_text, style_name = random.choice(FATALITY_STYLES)
        move = style_text.format(target=target, winner=nick)
        self.send_msg(channel, "\x034FINISH HIM!!")
        time.sleep(0.8)
        self.send_msg(channel, f"{nick} finishes {move}!")
        time.sleep(0.5)
        self.send_msg(channel, f"{nick} wins!")
        self.send_msg(channel, "\x034FATALITY")
        self.send_msg(channel, f"Total Kombatants killed: {counters['fatalities']}")

    def handle_hug(self, channel, nick, target):
        if not target:
            target = nick
        responses = [
            f"gives {target} a great big hug",
            f"looks at {target}.........then grabs {target} in a bear hug!",
            f"squeezes {target} so hard their eyes bulge",
            f"runs at {target} full speed and nearly knocks {target} over with a hug",
        ]
        self.send_action(channel, random.choice(responses))

    def handle_rhug(self, channel, nick, args):
        counters["hugs"] += 1
        save_counters(counters)
        target = self.random_nick(channel, exclude=nick)
        responses = [
            f"ACTION can't hug {target} quickly enough!",
            f"ACTION cries tears of joy as {target} hugs him",
            f"ACTION tackle-hugs {target} without warning",
            f"ACTION wraps both arms around {target} and refuses to let go",
        ]
        response = random.choice(responses)
        if response.startswith("ACTION "):
            self.send_action(channel, response[7:])
        else:
            self.send_msg(channel, response)
        self.send_msg(channel, f"Random people hugged to date: {counters['hugs']}")

    def handle_beer(self, channel, nick, target):
        if not target:
            target = self.random_nick(channel, exclude=nick)
            self.send_action(channel, f"tosses a cold beer to {nick}, no worries it's on {target}")
        else:
            self.send_action(channel, f"tosses a cold beer to {target}.")

    def handle_roulette(self, channel, nick, target):
        self.send_msg(channel, "*CLICK*")

    def handle_weed(self, channel, nick, args):
        self.send_msg(channel, f"{nick}, I'm allergic to weed.......ragweed, that is")

    def handle_condom(self, channel, nick, args):
        self.send_msg(channel, f"Random condom slogan: {random.choice(CONDOM_SLOGANS)}")

    def handle_rd20(self, channel, nick, args):
        counters["fights"] += 1
        save_counters(counters)
        target = self.random_nick(channel, exclude=nick)
        roll = random.randint(1, 20)
        result_text = RD20_RESULTS[-1][1]
        for threshold, text in RD20_RESULTS:
            if roll >= threshold:
                result_text = text
                break
        result_text = result_text.replace("{nick}", nick).replace("{target}", target)
        self.send_msg(channel, result_text)
        self.send_msg(channel, f"Random fights picked to date: {counters['fights']}")

    def handle_search(self, channel, nick, args):
        if not args.strip():
            self.send_msg(channel, f"{nick}: Search for what, genius?")
            return
        query = urllib.parse.quote_plus(args.strip())
        self.send_msg(channel, f"You will find the answer here: https://duckduckgo.com/?q={query}")

    # Active timebombs: channel -> {target, wire, thread, defused}
    _timebombs = {}

    def handle_timebomb(self, channel, nick, target):
        if not target:
            self.send_msg(channel, f"{nick}: Who are you bombing? !timebomb <nick>")
            return
        if channel in self._timebombs:
            self.send_msg(channel, "There's already a bomb ticking! Defuse it first!")
            return
        seconds = random.randint(20, 60)
        wire = random.choice(TIMEBOMB_WIRES)
        self._timebombs[channel] = {"target": target, "wire": wire, "defused": False}
        wire_list = " ".join(TIMEBOMB_WIRES)
        self.send_action(channel, f"stuffs the bomb into {target}'s pants. The display reads [{seconds}] seconds.")
        self.send_msg(channel, f"Defuse the bomb! Cut the correct wire by typing !cutwire <color>. There are {len(TIMEBOMB_WIRES)} wires. They are {wire_list}.")
        self.send_msg(channel, "\x034tic... tic... tic...")
        t = threading.Timer(seconds, self._bomb_explode, args=(channel, target))
        self._timebombs[channel]["thread"] = t
        t.start()

    def _bomb_explode(self, channel, target):
        if channel in self._timebombs and not self._timebombs[channel].get("defused"):
            self.send_msg(channel, f"\x034*BOOOM!* {target} is now in several pieces. Messy.")
            del self._timebombs[channel]

    def handle_cutwire(self, channel, nick, args):
        if channel not in self._timebombs:
            self.send_msg(channel, "There's no bomb ticking. Relax.")
            return
        bomb = self._timebombs[channel]
        guess = args.strip().capitalize()
        if guess == bomb["wire"]:
            bomb["defused"] = True
            bomb["thread"].cancel()
            del self._timebombs[channel]
            self.send_msg(channel, f"\x033{nick} cut the {guess} wire! The bomb is defused! Nice work, hero.")
        else:
            self.send_msg(channel, f"\x034WRONG WIRE! {nick} cut the {guess} wire... nothing happened. Yet. Keep trying.")

    def fetch_youtube_info(self, video_id):
        """Fetch YouTube video title and channel from the Data API."""
        key = CONFIG.get("youtube_api_key", "")
        if not key or key == "YOUR_YOUTUBE_API_KEY_HERE":
            return None
        url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet&id={urllib.parse.quote(video_id)}&key={key}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Prime1-IRC-Bot/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            items = data.get("items", [])
            if not items:
                return None
            snippet = items[0]["snippet"]
            title = snippet.get("title", "Unknown title")
            channel = snippet.get("channelTitle", "Unknown channel")
            return title, channel
        except Exception:
            return None

    def search_youtube(self, query):
        """Search YouTube and return top result."""
        key = CONFIG.get("youtube_api_key", "")
        if not key or key == "YOUR_YOUTUBE_API_KEY_HERE":
            return None
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={urllib.parse.quote(query)}&type=video&maxResults=1&key={key}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Prime1-IRC-Bot/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            items = data.get("items", [])
            if not items:
                return None
            item = items[0]
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            link = f"https://youtu.be/{video_id}"
            return title, channel, link
        except Exception:
            return None

    def handle_yt(self, channel, nick, args):
        """Handle .yt search query."""
        if not args.strip():
            self.send_msg(channel, f"{nick}: .yt what? Give me something to search for.")
            return
        threading.Thread(
            target=self._yt_search_worker,
            args=(channel, nick, args.strip()),
            daemon=True
        ).start()

    def _yt_search_worker(self, channel, nick, query):
        result = self.search_youtube(query)
        if result:
            title, ch, link = result
            self.send_msg(channel, f"[YouTube] {title} — {ch} → {link}")
        else:
            self.send_msg(channel, f"{nick}: Couldn't find anything for that. YouTube hates you.")

    def _yt_url_worker(self, channel, video_id, url):
        result = self.fetch_youtube_info(video_id)
        if result:
            title, ch = result
            self.send_msg(channel, f"[YouTube] {title} — {ch} → https://youtu.be/{video_id}")

    # GPT rate limiting
    _gpt_user_calls = {}          # nick -> [timestamp, ...] recent calls
    _gpt_global_last = 0          # timestamp of last global call
    _gpt_daily_count = 0          # calls made today
    _gpt_daily_reset = 0          # timestamp of last daily reset

    GPT_USER_BURST = 3            # calls allowed before cooldown kicks in
    GPT_USER_COOLDOWN = 180       # seconds cooldown after burst (3 minutes)
    GPT_GLOBAL_COOLDOWN = 6       # seconds between any calls (keeps under 10/min)
    GPT_DAILY_LIMIT = 230         # stop at 230 to leave buffer before 250 hard limit

    def _gpt_check_rate(self, channel, nick):
        """Check rate limits. Returns True if OK to proceed, False if limited."""
        now = time.time()
        nick_lower = nick.lower()

        # Reset daily counter at midnight
        today_start = now - (now % 86400)
        if self._gpt_daily_reset < today_start:
            self._gpt_daily_count = 0
            self._gpt_daily_reset = today_start

        # Daily limit check
        if self._gpt_daily_count >= self.GPT_DAILY_LIMIT:
            remaining = int(today_start + 86400 - now) // 3600
            self.send_msg(channel, f"{nick}: Daily GPT limit reached ({self.GPT_DAILY_LIMIT} calls). Resets in ~{remaining}h.")
            return False

        # Global cooldown
        since_global = now - self._gpt_global_last
        if since_global < self.GPT_GLOBAL_COOLDOWN:
            wait = int(self.GPT_GLOBAL_COOLDOWN - since_global) + 1
            self.send_msg(channel, f"{nick}: Too busy, wait {wait}s.")
            return False

        # Per-user burst + cooldown
        calls = self._gpt_user_calls.get(nick_lower, [])
        calls = [t for t in calls if now - t < self.GPT_USER_COOLDOWN]
        if len(calls) >= self.GPT_USER_BURST:
            wait = int(self.GPT_USER_COOLDOWN - (now - calls[0])) + 1
            mins = wait // 60
            secs = wait % 60
            time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
            self.send_msg(channel, f"{nick}: You've used your {self.GPT_USER_BURST} GPT calls. Cooldown expires in {time_str}.")
            return False

        # All good — update tracking
        calls.append(now)
        self._gpt_user_calls[nick_lower] = calls
        self._gpt_global_last = now
        self._gpt_daily_count += 1
        return True

    def handle_gpt(self, channel, nick, args):
        """Handle .gpt query using Gemini 2.5 Flash."""
        if not args.strip():
            self.send_msg(channel, f"{nick}: Ask me something.")
            return
        if not self._gpt_check_rate(channel, nick):
            return
        threading.Thread(
            target=self._gpt_worker,
            args=(channel, nick, args.strip()),
            daemon=True
        ).start()

    def _gpt_worker(self, channel, nick, query):
        key = CONFIG.get("gemini_api_key", "")
        if not key or key == "YOUR_GEMINI_API_KEY_HERE":
            self.send_msg(channel, f"{nick}: No Gemini API key configured.")
            return
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={key}"
        )
        prompt = (
            f"Answer this question in 1-2 complete sentences. "
            f"Be conversational and finish your thought completely. "
            f"No markdown, no bullet points, plain text only.\n\n"
            f"Question: {query}"
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 300,
                "temperature": 0.8,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }).encode()
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "Prime1-IRC-Bot/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Collapse newlines into spaces
            text = " ".join(text.split())
            # Truncate at last complete sentence if too long
            if len(text) > 450:
                truncated = text[:450]
                last_end = max(
                    truncated.rfind(". "),
                    truncated.rfind("! "),
                    truncated.rfind("? "),
                )
                if last_end > 50:
                    text = truncated[:last_end + 1].strip()
                else:
                    text = truncated[:447] + "..."
            self.send_msg(channel, f"[GPT] {text}")
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"[GPT] HTTP {e.code}: {body}")
            self.send_msg(channel, f"{nick}: Gemini HTTP {e.code} — check bot console for details.")
        except Exception as e:
            print(f"[GPT] Exception: {type(e).__name__}: {e}")
            self.send_msg(channel, f"{nick}: Something went wrong asking Gemini.")

    def handle_triggerme(self, channel, nick, args):
        commands = (
            "!8ball <question>, !gay <question>, !hug <nick>, !rhug, !pizza [nick/everyone], "
            "!soda [nick/everyone], !milk [nick], !shot [nick], !die <nick>, !beer [nick], "
            "!chuck, !bofh, !confucius, !dumblaws, !emo, !drunkbot, !weed, !condom, "
            "!roulette, !rd20, !search <term>, !timebomb <nick>, !cutwire <color>, "
            "!rcupcake, !cupcake <nick>, !rpickpocket, !ryomama, "
            "!fatality <nick>, !rfatality, !tests, .yt <search>, .gpt <question>"
        )
        self.send_notice(nick, f"Prime1's commands: {commands}")
        self.send_notice(nick, "Keyword triggers: prime1, hey right nut, hey left nut, stupid bot, stfu, who's your daddy, slap, and more. Just talk, I'm listening.")

    def handle_tests(self, channel, nick, args):
        test_list = ", ".join(f"!{t} <nick>" for t in sorted(TESTS.keys()))
        self.send_msg(channel, test_list)

    # ----------------------------------------------------------
    # COMMAND DISPATCH
    # ----------------------------------------------------------

    COMMANDS = {
        "!8ball":        (handle_8ball,      "args"),
        "!gay":          (handle_gay,        "args"),
        "!hug":          (handle_hug,        "target"),
        "!rhug":         (handle_rhug,       "args"),
        "!pizza":        (handle_pizza,      "target"),
        "!soda":         (handle_soda,       "target"),
        "!milk":         (handle_milk,       "target"),
        "!shot":         (handle_shot,       "target"),
        "!die":          (handle_die,        "target"),
        "!chuck":        (handle_chuck,      "args"),
        "!bofh":         (handle_bofh,       "args"),
        "!confucius":    (handle_confucius,  "args"),
        "!dumblaws":     (handle_dumblaws,   "args"),
        "!emo":          (handle_emo,        "args"),
        "!drunkbot":     (handle_drunkbot,   "args"),
        "!beer":         (handle_beer,       "target"),
        "!roulette":     (handle_roulette,   "target"),
        "!weed":         (handle_weed,       "args"),
        "!condom":       (handle_condom,     "args"),
        "!rd20":         (handle_rd20,       "args"),
        "!search":       (handle_search,     "args"),
        "!timebomb":     (handle_timebomb,   "target"),
        "!cutwire":      (handle_cutwire,    "args"),
        "!rfatality":    (handle_rfatality,  "args"),
        "!rcupcake":     (handle_rcupcake,   "args"),
        "!cupcake":      (handle_cupcake,    "target"),
        "!rpickpocket":  (handle_rpickpocket,"args"),
        "!ryomama":      (handle_ryomama,    "args"),
        "!fatality":     (handle_fatality,   "target"),
        "!triggerme":    (handle_triggerme,  "args"),
        "!tests":        (handle_tests,      "args"),
        "!prime":        (None,              "special"),
        ".yt":           (handle_yt,         "args"),
        ".gpt":          (handle_gpt,        "args"),
    }

    def dispatch_command(self, channel, nick, cmd, args):
        """Route a !command to its handler."""
        cmd_lower = cmd.lower()

        # % tests
        test_name = cmd_lower.lstrip("!")
        if test_name in TESTS:
            target = args.strip() if args.strip() else nick
            self.handle_test(channel, nick, test_name, target)
            return

        if cmd_lower not in self.COMMANDS:
            return

        handler, arg_type = self.COMMANDS[cmd_lower]

        if cmd_lower == "!prime":
            # !prime with no args = name trigger; with args = deflect
            if args.strip():
                self.send_msg(channel, "Say what?")
            else:
                self.send_msg(channel, "That's my name, don't wear it out.")
            return

        if arg_type == "args":
            handler(self, channel, nick, args.strip())
        else:  # target
            handler(self, channel, nick, args.strip() or None)

    # ----------------------------------------------------------
    # MESSAGE HANDLER
    # ----------------------------------------------------------

    def handle_privmsg(self, nick, channel, message):
        """Main message handler — commands first, then keyword triggers."""
        if not channel.startswith("#"):
            return  # ignore PMs for now
        if nick.lower() == CONFIG["nick"].lower():
            return

        msg = message.strip()

        # Detect ACTION messages (/me slaps prime1)
        is_action = msg.startswith("\x01ACTION ") and msg.endswith("\x01")
        if is_action:
            msg = msg[8:-1].strip()

        msg_lower = msg.lower()

        # YouTube URL detection — runs in background, no flood check needed
        if not is_action:
            yt_match = re.search(
                r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})',
                msg
            )
            if yt_match:
                video_id = yt_match.group(1)
                threading.Thread(
                    target=self._yt_url_worker,
                    args=(channel, video_id, msg),
                    daemon=True
                ).start()

            # Dot commands (.yt, .gpt)
            if msg.startswith("."):
                parts = msg.split(None, 1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                if cmd in self.COMMANDS:
                    self.dispatch_command(channel, nick, cmd, args)
                return

            # Bang commands (!8ball, !chuck, etc.)
            if msg.startswith("!"):
                parts = msg.split(None, 1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                self.dispatch_command(channel, nick, cmd, args)
                return

        # Keyword triggers — fire for both normal and ACTION messages
        if self.flood_ok():
            for pattern, responses in KEYWORD_TRIGGERS:
                if re.search(pattern, msg_lower):
                    response = random.choice(responses)
                    self.respond(channel, nick, response)
                    return

    # ----------------------------------------------------------
    # IRC EVENT LOOP
    # ----------------------------------------------------------

    def handle_line(self, line):
        print(f"<< {line}")

        # PING/PONG
        if line.startswith("PING"):
            self.send_raw("PONG " + line[5:])
            return

        parts = line.split(" ", 3)
        if len(parts) < 2:
            return

        prefix = parts[0].lstrip(":")
        command = parts[1]

        # Welcome — join channels
        if command == "001":
            self.connected = True
            self.send_msg("NickServ", f"IDENTIFY {CONFIG['nickserv_password']}")
            for ch in CONFIG["channels"]:
                self.send_raw(f"JOIN {ch}")

        # Nick list for channel
        elif command == "353":
            channel = parts[3].split()[0].lstrip("=@").lower()
            nicks_raw = parts[3].split(":", 1)[1].split()
            nicks = [n.lstrip("@+%&~") for n in nicks_raw]
            # Clear list on first 353 to avoid duplicates on rejoin
            if channel not in self._nick_list_building:
                self.channels[channel] = []
                self._nick_list_building.add(channel)
            self.channels[channel].extend(nicks)

        # End of names list
        elif command == "366":
            channel = parts[3].split()[0].lower()
            self._nick_list_building.discard(channel)

        # JOIN
        elif command == "JOIN":
            channel = parts[2].lstrip(":").lower()
            joining_nick = prefix.split("!")[0]
            self.channels.setdefault(channel, [])
            if joining_nick not in self.channels[channel]:
                self.channels[channel].append(joining_nick)

        # PART / QUIT
        elif command in ("PART", "QUIT"):
            leaving_nick = prefix.split("!")[0]
            for ch in self.channels:
                if leaving_nick in self.channels[ch]:
                    self.channels[ch].remove(leaving_nick)

        # NICK change
        elif command == "NICK":
            old_nick = prefix.split("!")[0]
            new_nick = parts[2].lstrip(":")
            for ch in self.channels:
                if old_nick in self.channels[ch]:
                    self.channels[ch].remove(old_nick)
                    self.channels[ch].append(new_nick)

        # KICK
        elif command == "KICK":
            channel = parts[2].lower()
            kicked_nick = parts[3].split()[0]
            if channel in self.channels and kicked_nick in self.channels[channel]:
                self.channels[channel].remove(kicked_nick)
            # Rejoin if we were kicked
            if kicked_nick.lower() == CONFIG["nick"].lower():
                time.sleep(3)
                self.send_raw(f"JOIN {channel}")

        # PRIVMSG
        elif command == "PRIVMSG":
            sender_nick = prefix.split("!")[0]
            target = parts[2]
            message = parts[3].lstrip(":") if len(parts) > 3 else ""
            self.handle_privmsg(sender_nick, target, message)

    def run(self):
        buffer = ""
        while self.running:
            try:
                self.connect()
                print(f"[Prime1] Connected to {CONFIG['server']}:{CONFIG['port']}")
                while self.running:
                    try:
                        data = self.sock.recv(4096).decode("utf-8", errors="replace")
                        if not data:
                            raise ConnectionResetError("Server closed connection")
                        buffer += data
                        while "\r\n" in buffer:
                            line, buffer = buffer.split("\r\n", 1)
                            self.handle_line(line)
                    except socket.timeout:
                        self.send_raw("PING :keepalive")
            except Exception as e:
                print(f"[Prime1] Disconnected: {e}")
                self.connected = False
                self.channels = {}
                if self.sock:
                    try:
                        self.sock.close()
                    except:
                        pass
                if self.running:
                    print(f"[Prime1] Reconnecting in {CONFIG['reconnect_delay']}s...")
                    time.sleep(CONFIG["reconnect_delay"])


if __name__ == "__main__":
    bot = Prime1Bot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n[Prime1] Shutting down.")
        bot.running = False
