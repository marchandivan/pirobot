import math

from PIL import Image, ImageDraw

image = Image.new("RGB", (320, 240), "WHITE")
draw = ImageDraw.Draw(image)


class EyeGenerator(object):
    moods = {
        "scared": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=0, pupil_pos=0.4, pupil_size=0.3,
                                        eye_brows_angle=-20, eye_brows_height=0.8),
                          right_eye=dict(radius=60, x=240, y=130, pupil_angle=180, pupil_pos=0.4, pupil_size=0.3,
                                         eye_brows_angle=20,
                                         eye_brows_height=0.8)),
        "surprised": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.4,
                                        eye_brows_angle=-20, eye_brows_height=0.8),
                          right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.4,
                                         eye_brows_angle=20,
                                         eye_brows_height=0.8)),
        "relaxed": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.6,
                                      eye_brows_angle=0,
                                      eye_brows_height=0.4),
                        right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.6,
                                       eye_brows_angle=0,
                                       eye_brows_height=0.4)),
        "crazy": dict(left_eye=dict(radius=50, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.4,
                                    eye_brows_angle=-20,
                                    eye_brows_height=0.7),
                      right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.6,
                                     eye_brows_angle=20,
                                     eye_brows_height=0.2)),
        "sad": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.4, pupil_size=0.4,
                                 eye_brows_angle=-20,
                                 eye_brows_height=0.0),
                    right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.4, pupil_size=0.4,
                                   eye_brows_angle=20,
                                   eye_brows_height=0.0)),
        "angry": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.5,
                                    eye_brows_angle=20,
                                    eye_brows_height=0.2),
                      right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.5,
                                     eye_brows_angle=-20,
                                     eye_brows_height=0.2)),
        "mad": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.6,
                                  eye_brows_angle=30,
                                  eye_brows_height=0.3),
                    right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.6,
                                   eye_brows_angle=-30,
                                   eye_brows_height=0.3)),
        "ashamed": dict(left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.8, pupil_size=0.1,
                                      eye_brows_angle=-20,
                                      eye_brows_height=0.5),
                        right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.8, pupil_size=0.1,
                                       eye_brows_angle=20,
                                       eye_brows_height=0.5)),
        "tired": dict(
            left_eye=dict(radius=60, x=80, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.1,
                          eye_brows_angle=-5,
                          eye_brows_height=0.1),
            right_eye=dict(radius=60, x=240, y=130, pupil_angle=90, pupil_pos=0.0, pupil_size=0.1,
                           eye_brows_angle=5,
                           eye_brows_height=0.1)),
        "annoyed": dict(
            left_eye=dict(radius=60, x=80, y=130, pupil_angle=-90, pupil_pos=0.8, pupil_size=0.3,
                          eye_brows_angle=10,
                          eye_brows_height=0.0),
            right_eye=dict(radius=60, x=240, y=130, pupil_angle=-90, pupil_pos=0.8,
                           pupil_size=0.3, eye_brows_angle=-10,
                           eye_brows_height=0.0)),
        "happy": dict(
            left_eye=dict(radius=60, x=80, y=130, pupil_angle=-90, pupil_pos=0.6, pupil_size=0.6,
                          eye_brows_angle=-5,
                          eye_brows_height=0.5),
            right_eye=dict(radius=60, x=240, y=130, pupil_angle=-90, pupil_pos=0.6, pupil_size=0.6,
                           eye_brows_angle=5,
                           eye_brows_height=0.5)),
        "silly": dict(
            left_eye=dict(radius=60, x=80, y=130, pupil_angle=135, pupil_pos=1.0, pupil_size=0.5,
                          eye_brows_angle=-20,
                          eye_brows_height=0.1),
            right_eye=dict(radius=60, x=240, y=130, pupil_angle=-90, pupil_pos=1.0,
                           pupil_size=0.5, eye_brows_angle=0,
                           eye_brows_height=0.4))
    }

    def _generate_eye(draw, radius, x, y, pupil_angle=0, pupil_pos=0, pupil_size=0.5, eye_brows_angle=0,
                      eye_brows_height=0):
        # Outline
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=None, outline="black", width=3)

        # Pupil
        pupil_radius = radius * pupil_size
        pupil_x = x + math.cos(math.radians(pupil_angle)) * pupil_pos * (radius - pupil_radius)
        pupil_y = y + math.sin(math.radians(pupil_angle)) * pupil_pos * (radius - pupil_radius)
        draw.ellipse((pupil_x - pupil_radius, pupil_y - pupil_radius, pupil_x + pupil_radius, pupil_y + pupil_radius),
                     fill="black", width=3)

        # Eye brows
        eye_brows_x1 = x - radius * math.cos(math.radians(eye_brows_angle)) * 1.1
        eye_brows_y1 = (y - radius * (1 + eye_brows_height)) - math.sin(math.radians(eye_brows_angle)) * radius
        eye_brows_x2 = x + radius * math.cos(math.radians(eye_brows_angle)) * 1.1
        eye_brows_y2 = (y - radius * (1 + eye_brows_height)) + math.sin(math.radians(eye_brows_angle)) * radius
        draw.line((eye_brows_x1, eye_brows_y1, eye_brows_x2, eye_brows_y2), fill="black", width=int(radius * 0.17))

    @staticmethod
    def generate_eyes(mood):
        mood_args = EyeGenerator.moods.get(mood, EyeGenerator.moods["relaxed"])
        image = Image.new("RGB", (320, 240), "WHITE")
        draw = ImageDraw.Draw(image)
        EyeGenerator._generate_eye(draw, **mood_args["left_eye"])
        EyeGenerator._generate_eye(draw, **mood_args["right_eye"])
        return image

    @staticmethod
    def get_moods():
        return list(EyeGenerator.moods.keys())
