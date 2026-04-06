import ffmpeg
import sys


def loop(s):
    (
        ffmpeg.input(s)
        .filter('aloop', loop=3, size=10 * 48000)
        .output(s.replace('m4a', 'wav'))
        .run(cmd=['ffmpeg', '-hide_banner', '-y'])
    )


def run(s):
    (
        ffmpeg.input(s)
        .filter('atrim', end=6.3)
        .output(s.replace('wav', 'm4a'))
        .run(cmd=['ffmpeg', '-hide_banner', '-y'])
    )


for name in sys.argv[1:]:
    run(name)
