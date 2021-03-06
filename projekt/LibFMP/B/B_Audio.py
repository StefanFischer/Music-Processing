"""
Module: LibFMP.B.B_Audio
Author: Frank Zalkow, Meinard Mueller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP)
"""

import librosa
import soundfile as sf
import IPython.display as ipd
import pandas as pd


def read_audio(path, Fs=None, mono=False):
    """Reads an audio file

    Args:
        path: Path to audio file
        Fs: Resample audio to given sampling rate. Use native sampling rate if None.
        mono (bool): Convert multi-channel file to mono.

    Returns:
        x: Waveform signal
        Fs: Sampling rate
    """
    return librosa.load(path, sr=Fs, mono=mono)


def write_audio(path, x, Fs):
    """Writes an audio file

    Args:
        path: Path to audio file
        x: Waveform signal
        Fs: Sampling rate
    """
    sf.write(path, x, Fs)


def audio_player_list(signals, rates, width=270, height=40, columns=None, column_align='center'):
    """Generate list of audio players

    Notebook: B/B_PythonAudio.ipynb

    Args:
        signals: List of audio signals
        rates: List of sample rates
        width: Width of player (either number or list)
        height: Height of player (either number or list)
        columns: Column headings
        column_align: Left, center, right
    """
    pd.set_option('display.max_colwidth', None)

    if isinstance(width, int):
        width = [width] * len(signals)
    if isinstance(height, int):
        height = [height] * len(signals)

    audio_list = []
    for cur_x, cur_Fs, cur_width, cur_height in zip(signals, rates, width, height):
        audio_html = ipd.Audio(data=cur_x, rate=cur_Fs)._repr_html_()
        audio_html = audio_html.replace('\n', '').strip()
        audio_html = audio_html.replace('<audio ', f'<audio style="width: {cur_width}px; height: {cur_height}px" ')
        audio_list.append([audio_html])

    df = pd.DataFrame(audio_list, index=columns).T
    table_html = df.to_html(escape=False, index=False, header=bool(columns))
    table_html = table_html.replace('<th>', f'<th style="text-align: {column_align}">')
    ipd.display(ipd.HTML(table_html))
