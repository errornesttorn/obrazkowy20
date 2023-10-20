import time
import copy
import datetime
import discord
import openai
import requests
import BingImageCreator

print("Wersja z 20 października 2023")

OPENAIAPIKEY = "sk-EBELEgGQoAl5Czm5BFVxT3BlbkFJpIOSzKvL5E"
DISCORDTOKEN = 'MTEwMzMxNDEwMDg0ODY5NzM5NQ.Gpa4_P.8GA-9-mNechsER0RoMYmKnHYa9cF'
BINGAPIKEY = "1RyTnuvfpTRQyOg1ih4Dg7u0U9PkRNKVXkW87pKjw6hT9Gq-jEiEJJpvYbGfM78Rmm5R5kB64ArgUHdsUOX1lD38cxuQJZ10k7AX_CmGU8397teGg3VbEsZmkTAZxcz9jYBmXpCHgV0DOAVNlg9T606R_o5Px2gufzLm8WbcbEYsiMnGvuyAsCSN_FJFgeYJM1S4xkl2Z2v7yV9J8-hikPhSK_rf4SI-M8"

with open("turbo_keys.txt", "r", encoding="utf-8") as f:
    temp = f.read()
    temp = temp.split("\n")
    OPENAIAPIKEY = temp[0]
    DISCORDTOKEN = temp[1]
    BINGAPIKEY = temp[2]

OPENAIAPIKEY += input("Extend the OPENAIAPIKEY: ")
DISCORDTOKEN += input("Extend the DISCORDTOKEN: ")
BINGAPIKEY += input("Extend the BINGAPIKEY: ")


openai.api_key = OPENAIAPIKEY
ostatia_wiadomosc = datetime.datetime.now()

users = [
    "indy (also known as indyrefentyzm or Natalka) should be depicted as a young woman with black long hair. She always dresses in black, wears tights, and a coat. Her main color scheme is black. Draw her in a realistic style.",
    "Ryż (also known as Ola) is a cute girl that is really into anime. She wears skirts, knee-socks, and a cute top. Her favorite color is pink. Draw her in a colorful anime style.",
    "Eryk (also known as Eryk Roch, or Eryk Groch) is an investor from Warsaw. Draw him as a rich, handsome, confident male in a realistic style. He likes money and investments. His theme color is brown.",

]

historia = []


def remove_non_latin_letters(string: str):
    # Define the valid characters as a set
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
    # Initialize an empty list to store the filtered characters
    filtered_chars = []
    # Loop through each character in the string
    for char in string:
        # If the character is in the valid set, append it to the filtered list
        if char in valid_chars:
            filtered_chars.append(char)
    # Join the filtered list into a new string and return it
    return "".join(filtered_chars)


def remove_tag(string: str) -> str:
    # define the tag to be removed
    tag = "<@1103314100848697395>"
    # replace the tag with an empty string
    new_string = string.replace(tag, "")
    # return the new string
    return new_string


def completion_api(prompt, engine="gpt-3.5-turbo-instruct", temperature=0.0, max_new_tokens=1024, stop=None):
    try:
        komplicja = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            stop=stop
        ).choices[0].text
    except:
        print("There was a problem. Waiting for 1 second")
        time.sleep(1)
        try:
            komplicja = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                stop=stop
            ).choices[0].text
        except:
            print("There was a problem. Waiting for 12 second")
            time.sleep(12)
            komplicja = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                stop=stop
            ).choices[0].text
    return komplicja

# assistant nazywa się Output
# dzienniki zawierają name i content
def prompt_generation(historia: dict) -> str:
    print("Historia, której używamy:")
    print(historia)
    try:
        with open("turbo_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
    except:
        print("Nie udało się otworzyć pliku turbo_prompt.txt")
        raise FileNotFoundError("Nie udało się otworzyć pliku turbo_prompt.txt")
    for wiadomosc in historia:
        kontent = remove_tag(wiadomosc['content'])
        prompt += "\n" + wiadomosc['name'] + ": " + kontent
    prompt += "\nOutput:"
    komplicja = completion_api(prompt, temperature=0.7, stop=["\n"])[1:]
    historia.append({"name": "Output", "content": komplicja})
    print("Wygenerowana komplicja:")
    print(komplicja)
    return komplicja


def bingPicture(prompt, auth):
    gen = BingImageCreator.ImageGen(auth)
    image_urls = gen.get_images(prompt)
    print("Done")
    return image_urls[0]


def handle_response(historia: dict) -> str:
    auths = [BINGAPIKEY,
             BINGAPIKEY,
             BINGAPIKEY]
    temp = "url"
    for i in range(3):
        print("Próbuję. auth numer to: " + str(i))
        try:
            temp = bingPicture(prompt_generation(historia), auths[i])
            return temp
        except:
            pass
    return "url"


def is_difference_greater_than_12_hours(current_datetime, defined_datetime):
    time_difference = current_datetime - defined_datetime
    return abs(time_difference) > datetime.timedelta(hours=12)


# Send messages
async def send_message(message, name, user_message, is_private):
    global historia, ostatia_wiadomosc, BINGAPIKEY
    if not "<@1103314100848697395>" in user_message: # wtedy komenda
        dane = user_message.split("\n")
        if dane[0] == "help":
            await message.channel.send("Commends are:\n- help\n- send_the_history\n- change_the_bing_token")
        if dane[0] == "list":
            pass
        if dane[0] == "send_the_history":
            for wiadomosc in historia:
                await message.channel.send(str(wiadomosc))
        if dane[0] == "change_the_bing_token":
            BINGAPIKEY = dane[1]
        return
    if is_difference_greater_than_12_hours(datetime.datetime.now(), ostatia_wiadomosc):
        historia.clear()
    while len(historia) > 8:
        historia.pop(0)
    try:
        historia_idealna = copy.deepcopy(historia)
        historia_idealna.append({"name": name, "content": user_message})
        url = handle_response(historia_idealna)
        if url == "url":
            await message.channel.send("Nie udało się wybingować ani jednego linku. Jest to conajmniej sus")
        if len(url) > 200:
            await message.channel.send("Link jest jakiś pojebany. Prawdopodobnie nie jest nawet linkiem tylko całą stroną internetową. Spróbuj ponownie czy coś")
    except:
        await message.channel.send("Coś się spierdoliło podczas generowania obrazka. Spróbuj ponownie czy coś")
        return
    # Get the response from the url
    try:
        response = requests.get(url)
    except:
        await message.channel.send("Coś się spierdoliło podczas pobierania obrazka. Link pewnie nie jest linkiem. Spróbuj ponownie czy coś")
        return
    try:
        temp = response.status_code
    except:
        await message.channel.send('Nie ma czegoś takiego jak "response.status_code"')
        return
    if response.status_code == 200:
        # Get the file name from the url
        # file_name = url.split("/")[-1]
        # file_name = remove_non_latin_letters(file_name)
        file_name = "temp.png"
        # Save the response content as a file
        with open(file_name, "wb") as file:
            file.write(response.content)
        # Get the channel object from the channel id
        channel = message.channel
        # Check if the channel is valid
        if channel:
            # Create a discord file object from the file name
            discord_file = discord.File(file_name)
        # Send the file to the channel
            await channel.send(file=discord_file)
        else:
            print("Invalid channel id")
            return
    else:
        await message.channel.send("Invalid URL. The response code something is " + str(response.status_code) + ". You're truly gonna do something with this and not just try again until it works")
        return
    historia = copy.deepcopy(historia_idealna)
    ostatia_wiadomosc = datetime.datetime.now()
    return


def run_discord_bot():
    TOKEN = DISCORDTOKEN
    #client = discord.Client()

    intents = discord.Intents.default()
    #intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return
        # Make sure he doesn't respond to messages not directed to him
        if message.content == "":
            return
        # Get data about the user
        username = str(message.author)
        name = str(message.author.display_name) 
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # If the user message contains a '?' in front of the text, it becomes a private message
        if user_message[0] == '?':
            user_message = user_message[1:]  # [1:] Removes the '?'
            await send_message(message, name, user_message, is_private=True)
        else:
            await send_message(message, name, user_message, is_private=False)

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)


if __name__ == "__main__":
    run_discord_bot()
