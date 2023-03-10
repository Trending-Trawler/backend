import requests
import base64
import random
import os
import playsound

from settings import settings

# should contain same voices as in assets/voices.json
# not vest solution but it is efficient and is enough for now
# eventually we should have a database of voices as a single source of truth
voices = [
    "random",
    # DISNEY VOICES
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    "en_male_pirate",  # pirate
    "en_female_madam_leota",  # Madame Leota
    # ENGLISH VOICES
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    # EUROPE VOICES
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    # SOUTH AMERICA VOICES
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # ASIA VOICES
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
    # SINGING VOICES
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    # OTHER
    "en_male_narration",
    "en_male_funny",
    "en_male_cody",  # narrator  # wacky  # Serious
    "en_female_emotional",  # peaceful
    "en_female_ht_f08_glorious",  # Glorious
    "en_male_sing_funny_it_goes_up",  # It Goes Up
    "en_male_m2_xhxs_m03_silly",  # Chipmunk
    "en_female_ht_f08_wonderful_world",  # Dramatic
]


def tts(
    text_speaker: str = "random",
    req_text: str = "TikTok Text To Speech",
):
    if text_speaker == "random":
        i = random.randint(1, len(voices))
        text_speaker = voices[i]

    req_text = req_text.replace("+", "plus")
    req_text = req_text.replace(" ", "+")
    req_text = req_text.replace("&", "and")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Cookie": f"sessionid={settings.tiktok_session_id};",
    }
    url = f"https://tiktokv.com/media/api/text/speech/invoke/?text_speaker={text_speaker}&req_text={req_text}&speaker_map_type=0&aid=1233"
    r = requests.post(url, headers=headers)

    vstr = [r.json()["data"]["v_str"]][0]
    message = [r.json()["message"]][0]
    statuscode = [r.json()["status_code"]][0]
    log = [r.json()["extra"]["log_id"]][0]
    duration = [r.json()["data"]["duration"]][0]
    speaker = [r.json()["data"]["speaker"]][0]
    output_data = {
        "status": message.capitalize(),
        "status_code": statuscode,
        "duration": duration,
        "speaker": speaker,
        "log": log,
    }
    print(output_data)

    b64d = base64.b64decode(vstr)

    return b64d


def main():
    b64d = tts()
    filename = "voice.mp3"
    with open(filename, "wb") as out:
        out.write(b64d)
    playsound.playsound(filename)
    os.remove(filename)


if __name__ == "__main__":
    main()
