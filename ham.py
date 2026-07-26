import sys
import time

# ANSI escape codes for styling
white_bold = "\033[1;97m"
reset = "\033[0m"

# Clip starts at 1:48 (108s). Delay = song_timestamp_seconds - 108.
# [delay_from_clip_start, typing_speed_per_char, lyric_text]
lyrics = [
    [0.0,  0.06, "Have I been more sure"],
    [3.0,  0.07, "You're everything I wanted"],
    [7.0,  0.09, "You are my sun in my skies"],
    [10.0, 0.08, "You are the days in my nights, baby"],
    [15.0, 0.07, "You're everything I wanted"],
    [19.0, 0.09, "You are the reason I smile"],
    [21.0, 0.08, "You put the worth in my while, baby"],
    [26.0, 0.07, "You're everything I wanted"],
]
title = "GAW NI MARK"


def typewriter(text, speed):
    sys.stdout.write(white_bold)
    sys.stdout.flush()

    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(speed)

    sys.stdout.write(reset + "\n")
    sys.stdout.flush()


def main():
    print(title)
    print()

    start_time = time.time()

    for delay, speed, text in lyrics:
        # wait until it's time for this line (based on the video's timestamps)
        elapsed = time.time() - start_time
        wait = delay - elapsed
        if wait > 0:
            time.sleep(wait)

        typewriter(text, speed)


if __name__ == "__main__":
    main()