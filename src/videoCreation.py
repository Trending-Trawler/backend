import asyncio
import os
import re
import multiprocessing
from os.path import exists
from typing import Tuple, Any, Final

import playsound
import shutil
from typing import Tuple, Any
from PIL import Image

from operator import itemgetter
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.crop import crop
import random
import time

from tts import tts
from screenshots import create_screenshots
from comments import get_comments, get_title


def prepare_background(video_id, length, width=1080, height=1920):
    # path should be defined in config later
    video = VideoFileClip(f"../assets/videos/full/{video_id}.mp4").without_audio()
    vide_duration = video.duration

    random_start = random.randint(0, int(vide_duration))
    vid = video.subclip(random_start, random_start + length)
    video.close()

    vid_resized = resize(vid, height=height)
    clip = (
        vid_resized
    )
    # calculate the center of the background clip
    c = clip.w // 2

    # calculate the coordinates where to crop
    half_w = width // 2
    x1 = c - half_w
    x2 = c + half_w

    return crop(clip, x1=x1, y1=0, x2=x2, y2=height)


async def audio_clip(thread_url, voice_id):
    comments = await get_comments(thread_url)
    title = await get_title(thread_url)
    audio_list = []
    duration = 0
    comment_amount = 0
    b64d_title = tts(voice_id, title)
    filename = "voice.mp3"
    with open(filename, "wb") as out:
        out.write(b64d_title)
    clip = AudioFileClip(filename)
    duration = duration + clip.duration
    audio_list.append(clip)
    out.close()
    os.remove("voice.mp3")
    for comment in comments:
        if duration > 6000:
            break
        comment_amount = comment_amount + 1
        b64d_audio = tts(voice_id, comment.body)
        filename = "voice.mp3"
        with open(filename, "wb") as out:
            out.write(b64d_audio)
        clip = AudioFileClip(filename)
        duration = duration + clip.duration
        audio_list.append(clip)
        out.close()
        os.remove("voice.mp3")
    audio_concat = concatenate_audioclips(audio_list)
    # audio_composite = CompositeAudioClip([audio_concat])
    # audio_composite.fps = 44100
    # audio_composite.write_audiofile("audiofile.mp3")
    audio = {
        "audio_clips": audio_list,
        "audio_comp": CompositeAudioClip([audio_concat]),
        "duration": duration,
        "comments": comments,
        "comment_amount": comment_amount
    }
    return audio


async def make_final_video(
        thread_url,
        voice_id,
        video_id
):
    # can be defined in config file later
    CONST_WIDTH: Final[int] = 1080
    CONST_HIGHT: Final[int] = 1920
    opacity = 0.95

    # Gather all audio clips and duration
    audio = await audio_clip(thread_url, voice_id)
    comments, index, duration, audio_composite, audio_clips = \
        itemgetter("comments", "comment_amount", "duration", "audio_comp", "audio_clips")(audio)

    # Gather all images
    #while len(comments) > index:
     #   comments.pop(len(comments) - 1)
    image_list = await create_screenshots(thread_url, comments)

    print("Creating the final video 🎥")
    background_clip = prepare_background(video_id, duration, CONST_WIDTH, CONST_HIGHT)

    print(f"Video Will Be: {duration} Seconds Long")

    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

    screenshot_width = int((CONST_WIDTH * 90) // 100)

    image_clips = []


    for idx in range(index):
        image = image_list[idx]
        filename = f"image.jpeg"
        with open(filename, "wb") as out:
            out.write(image)
        print(audio_clips[idx].duration)
        comment = ImageClip(f"./image.jpeg").set_duration(audio_clips[idx].duration).set_opacity(new_opacity).set_position(
            "center")
        resized_comment = resize(comment, width=screenshot_width)
        image_clips.append(
            resized_comment
        )
        out.close()
        os.remove("./image.jpeg")

    image_concat = concatenate_videoclips(image_clips)  # note transition kwarg for delay in imgs
    image_concat.audio = audio_composite
    audio_composite.close()
    final = CompositeVideoClip([background_clip, image_concat.set_position("center")])
    image_concat.close()

    return final



async def main():
    await make_final_video("https://www.reddit.com/r/AskReddit/comments/ablzuq/people_who_havent_pooped_in_2019_yet_why_are_you/", "en_au_001", "minecraft")

if __name__ == "__main__":
    asyncio.run(main())