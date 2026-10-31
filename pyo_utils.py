import random
import numpy as np
import pygame

#############################################
#   Andrew Chao - andrewchao7000@gmail.com  #
#   6/1/2026                                #
#############################################

server = None

# Bright Plinko pentatonic frequencies (C5 to A6) for crisp percussive "plink" notes
PLINK_FREQS = [
    523.25,   # C5
    587.33,   # D5
    659.25,   # E5
    783.99,   # G5
    880.00,   # A5
    1046.50,  # C6
    1174.66,  # D6
    1318.51,  # E6
    1567.98,  # G6
    1760.00,  # A6
]

_PLINK_SOUNDS = []
_MIXER_READY = False


def _init_plink_sounds():
    global _MIXER_READY, _PLINK_SOUNDS
    if _MIXER_READY:
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(24)

        sr = pygame.mixer.get_init()[0]
        channels = pygame.mixer.get_init()[2]
        duration = 0.22
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)

        # Fast percussive attack (2ms)
        attack = np.minimum(1.0, t / 0.002)

        _PLINK_SOUNDS = []
        for freq in PLINK_FREQS:
            # Fundamental + xylophone/peg chime overtones + crisp mallet strike transient
            fund = np.sin(2 * np.pi * freq * t) * np.exp(-t * 16.0)
            overtone1 = 0.45 * np.sin(2 * np.pi * (freq * 2.0) * t) * np.exp(-t * 35.0)
            overtone2 = 0.25 * np.sin(2 * np.pi * (freq * 2.76) * t) * np.exp(-t * 55.0)
            click = 0.20 * np.sin(2 * np.pi * (freq * 4.2) * t) * np.exp(-t * 140.0)

            wave = attack * (fund + overtone1 + overtone2 + click)
            wave = wave / np.max(np.abs(wave)) * 0.85
            samples = (wave * 32767).astype(np.int16)

            if channels == 2:
                samples = np.column_stack((samples, samples))

            sound = pygame.sndarray.make_sound(samples)
            _PLINK_SOUNDS.append(sound)

        _MIXER_READY = True
        return True
    except Exception as e:
        print(f"Warning: Could not initialize plink audio mixer: {e}")
        return False


def play_bounce_sound(volume):
    if not _MIXER_READY:
        if not _init_plink_sounds():
            return

    if not _PLINK_SOUNDS:
        return

    sound = random.choice(_PLINK_SOUNDS)
    channel = pygame.mixer.find_channel(True)
    if channel is not None:
        clamped_vol = max(0.15, min(1.0, float(volume)))
        channel.set_volume(clamped_vol)
        channel.play(sound)
