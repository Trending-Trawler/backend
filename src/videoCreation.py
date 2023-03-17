import asyncio
import os
from io import BytesIO
from tempfile import TemporaryFile

import multiprocessing
from operator import itemgetter
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.crop import crop
import random

from tts import tts
from screenshots import create_screenshots
from comments import get_comments
from settings import settings


def prepare_background(video_id, length, width=1080, height=1920):
    # path should be defined in config later
    video = VideoFileClip(f"assets/videos/full/{video_id}").without_audio()

    vide_duration = video.duration

    random_start = random.randint(0, int(vide_duration))
    vid = video.subclip(random_start, random_start + length)
    video.close()

    vid_resized = resize(vid, height=height)
    clip = vid_resized
    # calculate the center of the background clip
    c = clip.w // 2

    # calculate the coordinates where to crop
    half_w = width // 2
    x1 = c - half_w
    x2 = c + half_w

    return crop(clip, x1=x1, y1=0, x2=x2, y2=height)


async def audio_clip(thread_url, voice_id):
    comments, title = await get_comments(thread_url)
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
        if duration > 2000:
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
        "comment_amount": comment_amount,
    }
    return audio


async def create_final_video(thread_url, voice_id, video_id):
    # can be defined in config file later
    CONST_WIDTH = 1080
    CONST_HIGHT = 1920
    opacity = 0.95

    # Gather all audio clips and duration
    audio = await audio_clip(thread_url, voice_id)
    comments, index, duration, audio_composite, audio_clips = itemgetter(
        "comments", "comment_amount", "duration", "audio_comp", "audio_clips"
    )(audio)

    screenshots = await create_screenshots(thread_url, comments)

    print("Creating the final video 🎥")
    background_clip = prepare_background(video_id, duration, CONST_WIDTH, CONST_HIGHT)

    print(f"Video Will Be: {duration} Seconds Long")

    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

    screenshot_width = int((CONST_WIDTH * 90) // 100)

    image_clips = []

    for i in range(len(comments) + 1):
        image = screenshots[i]
        filename = "image.jpeg"
        with open(filename, "wb") as out:
            out.write(image)
        print(audio_clips[i].duration)
        comment = (
            ImageClip("./image.jpeg")
            .set_duration(audio_clips[i].duration)
            .set_opacity(new_opacity)
            .set_position("center")
        )
        resized_comment = resize(comment, width=screenshot_width)
        image_clips.append(resized_comment)
        out.close()
        os.remove("./image.jpeg")

    image_concat = concatenate_videoclips(
        image_clips
    )  # note transition kwarg for delay in imgs
    image_concat.audio = audio_composite
    audio_composite.close()
    final = CompositeVideoClip([background_clip, image_concat.set_position("center")])
    image_concat.close()

    final.write_videofile(
        "assets/final.mp4",
        fps=int(24),
        audio_codec="aac",
        audio_bitrate="192k",
        threads=multiprocessing.cpu_count(),
    )
    final.close()


async def main():
    await create_final_video(
        settings.reddit_thread_url,
        settings.voice_id,
        settings.video_id,
    )


if __name__ == "__main__":
    asyncio.run(main())
