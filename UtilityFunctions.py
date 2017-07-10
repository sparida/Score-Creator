import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd

from SoundGenerator import *

SAMPLE_RATE = 11250 # Overall sampling rate
TOTAL_WHOLE_NOTES = 16 # Maximum length of a music score
TOTAL_EIGHTH_NOTES = TOTAL_WHOLE_NOTES * 8 # Maximum number of eigth notes in a music score

# Note characters without specific octyav number
octave1Notes       = [ "C"  , "Db" , "D"  , "Eb" , "E"  , "F"  , "Gb"  , "G"  , "Ab" , "A"  , "Bb" , "B" ]
# Note frequencies for the first octave
octave1Frequencies = [ 32.70, 34.65, 36.71, 38.89, 41.20, 43.65,  46.25, 49.00, 51.91, 55.00, 58.27, 61.74 ]
# Dictionary of the two lists above
octave1Dict        = dict(zip(octave1Notes, octave1Frequencies))


# Note Lengths (Total number of 8th notes in each note type)
WHOLE_NOTE   = 8
HALF_NOTE    = 4
QUARTER_NOTE = 2
EIGHTH_NOTE  = 1 # Smallest possible note length

# Convert time in millisecs to number of smaples needed to fill that duration
def convertTimeToSampleCount(time):
	return int(time / (1000.0/SAMPLE_RATE))

# Return the duration of an eigth note in secs	
def getDurationOf8thNote(tempo):
	return 30.0/tempo

# Return the frequency of a note based on note character and octave number
# Works on the principle that frequency of the same note character an octave higher is twice that of the current octave
# Example : Frequncy of C2 = 2 x Frequency of C1	
def getNoteFrequency(noteChar, octave):
	baseFrequency        = octave1Dict[noteChar]
	octaveBasedFrequency = baseFrequency * ( 2**(octave - 1) )
	return octaveBasedFrequency

# Takes the note character, current octave and the number of halfsteps and returns the pitch changed note data
# HalfSteps: +ve = Pitch Up, -ve = Pitch Down
def getPitchChangedData(noteChar, octave, halfSteps):
		
	octaveChange   = floor(float(halfSteps) / 12.0)
	noteTypeChange = halfSteps % 12
		
	newOctave = octave + octaveChange
	newChar   = octave1Notes[octave1Notes.index(noteChar) + noteTypeChange]
	
	return(newChar, newOctave)

# Takes a SoundGenerator Object and writes the sound array as a wav file	
def writeWAVToFile(soundObj, filename):
	write(filename + ".wav", SAMPLE_RATE, soundObj.getSound())

# Limits the values in the sound array of a Sound Genrastor object to within -1.0 and 1.0	
def limitAmplitude(amplitude):
	return max(min(float(amplitude), 1.0), -1.0)
