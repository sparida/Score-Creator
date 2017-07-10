import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd

from SoundGenerator import SoundGenerator
from UtilityFunctions import *

# Class to handle note properties and genrate sound for each note using tempo and an envelope
class Note:
	def __init__(self, noteValue = "C4", velocity = 1.0, startLocation = 0, noteLength = 32, waveType = "Sine"):
		self.noteValue = noteValue # Actual note 
		self.velocity = abs(limitAmplitude(velocity)) # Note Loudness
		self.startLocation = startLocation # Number representing 8th Note Count for the start of note
		self.noteLength = noteLength # Note length in number fo 8th Notes
		self.octave   = int(self.noteValue[-1])# Note Octave
		self.noteChar = self.noteValue[0] if(len(noteValue) == 2) else self.noteValue[:2] # Note Character
		self.noteFrequency = getNoteFrequency(self.noteChar, self.octave) # Actual note frequency
		self.waveType = waveType

		
	# Return a note with changed pitch based on number fo half steps: +ve = Pitch Up, -ve = Pitch Down	
	def pitchChange(self, halfSteps):
		newChar, newOctave = getPitchChangedData(self.noteChar, self.octave, halfSteps)
		noteValue = newChar + str(newOctave)
		return Note(noteValue, self.velocity, self.startLocation, self.noteLength, self.waveType)
	
	# Genrate note sound
	# Each note sound takes up the entire length of the score
	# If a note doesnt start at location 0 it will have silence till its start location and silence after it ends
	# Each of these notes are suprimposed directly to genrate final music
	
	def getNoteSound(self, tempo, envelope, applyEnvelope):
	
		# The duration of the smallest possible length of a note base don the tempo: in secs
		lengthOf8      = getDurationOf8thNote(tempo)
		
		# The duration of the actual note in secs
		# Note length is a the number of eighths making up the note
		duration       = self.noteLength * float(lengthOf8)
		
		# The duration of the initial silence in the sound before the note starts
		initDuration   = self.startLocation   * float(lengthOf8)
		
		# The duration of teh silence in the entire sound after the note ends
		# We need this as we want each note sound to take up the entire possible score length 
		# This enabkes us to directly superimpose note sounds to get the final music 
		endDuration    = max((TOTAL_EIGHTH_NOTES - (self.startLocation + self.noteLength)) * float(lengthOf8), 0)
		
		# Generate initial silence
		initialSilence = SoundGenerator(waveType = "Constant",    frequency = 5, amplitude = 0.0, duration = initDuration)
		
		# Generate sound of note based on note attributes
		soundPart      = SoundGenerator(waveType = self.waveType, frequency = self.noteFrequency, amplitude = self.velocity, duration = duration)

		if applyEnvelope:

			# Obtain the ADSR Enevelope to shape note sound from the envelope object
			# Note that the ADSR envelope object is just a regular Sound Generator Object
			adsrEnvelope   = envelope.getADSREnvelope(soundPart)
			# Apply enevelope to shape note sound using the ** operator

			soundPart       = adsrEnvelope ** soundPart
		# Generate end silence if any
		endSilence     = SoundGenerator(waveType = "Constant",    frequency = 5, amplitude = 0.0, duration = endDuration)
		
		# Join all 3 sounds togetehr to get final note sound
		return initialSilence ^ soundPart ^ endSilence
	
	# String repsentation of note attributes used in writeScore method of ScoreManager
	def __str__(self):
		return "N:" + self.noteValue + "|V:" + str(self.velocity) + "|S:" + str(self.startLocation) + "|L:" + str(self.noteLength) + "|W:" + self.waveType


if __name__ == "__main__":		
	note1= Note(noteValue = "C4", velocity = 1.0, startLocation = 16, noteLength = 1, waveType = "Sine")
	note2 = note1.pitchChange(0)
	print(note1)
	print(note2)
	noteSound = note2.getNoteSound(100)
	writeWAVToFile(noteSound, "noteSound")