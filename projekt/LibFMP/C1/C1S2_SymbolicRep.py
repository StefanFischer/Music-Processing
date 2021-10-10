"""
Module: LibFMP.C1.C1S2_SymbolicRep
Author: Frank Zalkow, Meinard Müller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP)
"""
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import patches
import pretty_midi
import music21 as m21
import sys
sys.path.append('..')
import LibFMP.B

def csv_to_list(csv):
    """Convert a csv score file to a list of note events

    Notebook: C1/C1S2_CSV.ipynb

    Args:
        csv: Either a path to a csv file or a data frame

    Returns:
        score: A list of note events where each note is specified as
               [start, duration, pitch, velocity, label]
    """

    if isinstance(csv, str):
        df = LibFMP.B.read_csv(csv)
    elif isinstance(csv, pd.DataFrame):
        df = csv
    else:
        raise RuntimeError('csv must be a path to a csv file or pd.DataFrame')

    score = []
    for i, (start, duration, pitch, velocity, label) in df.iterrows():
        score.append([start, duration, pitch, velocity, label])
    return score


def midi_to_list(midi):
    """Convert a midi file to a list of note events

    Notebook: C1/C1S2_MIDI.ipynb

    Args:
        midi: Either a path to a midi file or a data frame

    Returns:
        score: A list of note events where each note is specified as
               [start, duration, pitch, velocity, label]
    """

    if isinstance(midi, str):
        midi_data = pretty_midi.pretty_midi.PrettyMIDI(midi)
    elif isinstance(midi, pd.DataFrame):
        midi_data = midi
    else:
        raise RuntimeError('midi must be a path to a midi file or pretty_midi.PrettyMIDI')

    score = []

    for instrument in midi_data.instruments:
        for note in instrument.notes:
            start = note.start
            duration = note.end - start
            pitch = note.pitch
            velocity = note.velocity / 128.
            score.append([start, duration, pitch, velocity, instrument.name])
    return score


def xml_to_list(xml):
    """Convert a music xml file to a list of note events

    Notebook: C1/C1S2_MusicXML.ipynb

    Args:
        xml: Either a path to a music xml file or a music21.stream.Score

    Returns:
        score: A list of note events where each note is specified as
               [start, duration, pitch, velocity, label]
    """

    if isinstance(xml, str):
        xml_data = m21.converter.parse(xml)
    elif isinstance(xml, m21.stream.Score):
        xml_data = xml
    else:
        raise RuntimeError('midi must be a path to a midi file or music21.stream.Score')

    score = []

    for part in xml_data.parts:
        instrument = part.getInstrument().instrumentName

        for note in part.flat.notes:

            if note.isChord:
                start = note.offset
                duration = note.quarterLength

                for chord_note in note.pitches:
                    pitch = chord_note.ps
                    volume = note.volume.realized
                    score.append([start, duration, pitch, volume, instrument])

            else:
                start = note.offset
                duration = note.quarterLength
                pitch = note.pitch.ps
                volume = note.volume.realized
                score.append([start, duration, pitch, volume, instrument])

    score = sorted(score, key=lambda x: (x[0], x[2]))
    return score


def list_to_csv(score, fn_out):
    """Convert a list of note events to a csv file

    Notebook: C1/C1S2_CSV.ipynb

    Args:
        score: List of note events
        fn_out: The path of the csv file to be created
    """
    df = pd.DataFrame(score, columns=['Start', 'Duration', 'Pitch', 'Velocity', 'Instrument'])
    # ideally, I would like to use float_format='%.3f', but then the numeric columns are considered as strings and,
    # therefore, are quoted
    df.to_csv(fn_out, sep=';', index=False, quoting=2)


def visualize_piano_roll(score, xlabel='Time (seconds)', ylabel='Pitch', colors='FMP_1', velocity_alpha=False,
                         figsize=(12, 4), ax=None, dpi=72):
    """Plot a pianoroll visualization

    Notebook: C1/C1S2_CSV.ipynb

    Args:
        score: List of note events
        xlabel: Label for x axis
        ylabel: Label for y axis
        colors: Several options: 1. string of FMP_COLORMAPS, 2. string of matplotlib colormap, 3. list or np.ndarray of
            matplotlib color specifications, 4. dict that assigns labels  to colors
        velocity_alpha (bool): Use the velocity value for the alpha value of the corresponding rectangle
        figsize: Width, height in inches
        ax: The Axes instance to plot on
        dpi: Dots per inch

    Returns:
        fig: The created matplotlib figure or None if ax was given.
        ax: The used axes
    """
    fig = None
    if ax is None:
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.subplot(1, 1, 1)

    labels_set = sorted(set([note[4] for note in score]))
    colors = LibFMP.B.color_argument_to_dict(colors, labels_set)

    pitch_min = min(note[2] for note in score)
    pitch_max = max(note[2] for note in score)
    time_min = min(note[0] for note in score)
    time_max = max(note[0] + note[1] for note in score)

    for start, duration, pitch, velocity, label in score:
        rect = patches.Rectangle((start, pitch - 0.5), duration, 1, linewidth=1,
                                 edgecolor='k', facecolor=colors[label], alpha=velocity)
        ax.add_patch(rect)

    ax.set_ylim([pitch_min - 1.5, pitch_max + 1.5])
    ax.set_xlim([min(time_min, 0), time_max + 0.5])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid()
    ax.set_axisbelow(True)
    ax.legend([patches.Patch(linewidth=1, edgecolor='k', facecolor=colors[key]) for key in labels_set],
              labels_set, loc='upper right', framealpha=1)

    if fig is not None:
        plt.tight_layout()

    return fig, ax
