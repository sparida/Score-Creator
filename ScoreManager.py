import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd

from SoundGenerator import SoundGenerator
from Note import Note
from UtilityFunctions import *
from Effects import Delay
from Envelope import Envelope

# Class to manage actual creation of music
class ScoreManager():
	
	# Set the tempo, overall envelope control
	def __init__(self, tempo = 100, envelope = Envelope(1, 1, 1.0, 1), apply = True):
		self.tempo = int(tempo)
		self.envelope = envelope
		self.applyEnvelope = apply
		self.notes = []
		
	# Add note to the collection of notes, each note is treated individually and is made of silence + noteSound + silence	
	def addNote(self, note):
		self.notes.append(note)
		
	def removeNote(self, clickXGrid, noteValue):
		removeIndices = []
		
		for i in range(len(self.notes)):
			note = self.notes[i]
			if(note.noteValue == noteValue and note.startLocation <= clickXGrid and clickXGrid < (note.startLocation + note.noteLength ) ):
				removeIndices.append(i)
		self.notes = [self.notes[i] for i in range(len(self.notes)) if i not in removeIndices]
		return removeIndices
		
	# Parse a given striong to obtain note attributes
	def parseNoteString(self, noteStr):
		# Split note string
		vals = noteStr.split('|')

		# Obtain note attributes
		noteValue     = str(vals[0].split(':')[1])
		velocity      = float(vals[1].split(':')[1])
		startLocation = int(vals[2].split(':')[1])
		noteLength    = int(vals[3].split(':')[1])
		waveType      = str(vals[4].split(':')[1])

		# Instantiate new note and return it
		note = Note(noteValue, velocity, startLocation, noteLength, waveType)
		return note
		
	# Read score file to populate notes list
	def readScore(self, filename):
		with open(filename, "r") as infile:
			noteStrings = infile.readlines()
			noteStrings = [n.strip() for n in noteStrings]
			for noteString in noteStrings:
				if noteString[0] == '#':
					continue
				self.addNote(self.parseNoteString(noteString))
	
	# Write notes list as a score file
	def writeScore(self, filename):
		with open(filename, "w") as outfile:
			outStr = ""
			for note in self.notes:
				outStr += str(note) + '\n'
			outfile.write(outStr[:-1])
	
	# Empty list of notes
	def clear(self):
		self.notes = []
	
	# Set Tempo
	def setTempo(self, tempo):
		self.tempo = tempo

	# Return Tempo
	def getTempo(self):
		return self.tempo
		
	def setApplyEnvelope(self, apply):
		self.applyEnvelope = apply
	
	def setEnvelope(self, envelope):
		self.envelope = envelope

	# Generate sound for each note and superimpose to create music
	def generateSound(self):
		# Create empty sound object of max length
		initDuration   = TOTAL_EIGHTH_NOTES   * getDurationOf8thNote(self.tempo)
		finalSound = SoundGenerator(waveType = "Constant",    frequency = 5, amplitude = 0.0, duration = initDuration)
	
		# Add sound from each note to object
		for note in self.notes:
			finalSound = finalSound + note.getNoteSound(self.tempo, self.envelope, self.applyEnvelope)
		return finalSound
		
if __name__ == "__main__":
	env = Envelope(1, 1, 1.0, 1)
	sm = ScoreManager(300, env)
	sm.readScore("Snare.txt")
	soundObj = sm.generateSound()
	writeWAVToFile(soundObj, "chord1")
	delay = Delay(delayTime = 1000.0, repetitions = 10, mix = 0.5, decay = 1.0)
	ds = delay.generateDelayedSound(soundObj)
	writeWAVToFile(ds, "delayedchord1")



	"""
	snareEnv = Envelope(attack = 100, decay = 20, sustain = 0.5, release = 300)
	nm1 = ScoreManager(100, snareEnv)
	nm1.readScore("Snare.txt")
	ns1 = nm1.generateSound()
	writeWAVToFile(ns1, "Snare")
		
	
	kickEnv = Envelope(attack = 1, decay = 200, sustain = 0.0, release = 200)
	nm1 = ScoreManager(100, kickEnv)
	nm1.readScore("Kick.txt")
	ns1 = nm1.generateSound()
	writeWAVToFile(ns1, "Kick")
	
	env = Envelope(attack = 1000, decay = 200, sustain = 0.5, release = 400)

	tempo1 = 1600
	nm1 = ScoreManager(tempo1, env)
	nm1.readScore("InScore2.txt")
	ns1 = nm1.generateSound()
	writeWAVToFile(ns1, "NormalSound100")

	tempo2 = 3200
	nm2 = ScoreManager(tempo2, env)
	nm2.readScore("InScore2.txt")
	ns2 = nm2.generateSound()
	writeWAVToFile(ns2, "NormalSound200")
	
	delay = Delay(repetitions = 8, mix = 0.5)
	ds = delay.generateDelayedSound(ns1)
	
	writeWAVToFile(ds, "DelaySound")
	nm1.writeScore("OutScore.txt")
	"""
	
	"""
	sin1 = SoundGenerator(waveType = "Sine"  , duration = 3.0)
	sqr1 = SoundGenerator(waveType = "Square", frequency = 400.0, amplitude = 0.2, duration = 3.0)
	sqr2 = SoundGenerator(waveType = "Square", frequency = 500.0, amplitude = 0.2, duration = 3.0)
	saw1 = SoundGenerator(waveType = "Sawtooth"  , duration = 3)
	
	note1 = SoundGenerator(waveType = "Sine", frequency = 400.0, amplitude = 0.5, duration = 2.0)
	env = Envelope(attack = 10, decay = 10, sustain = 0.0, release = 10)
	adsrEnvelope = env.getADSREnvelope(note1)
	envNote = adsrEnvelope ** note1
	writeWAVToFile(note1, "note1")
	writeWAVToFile(adsrEnvelope, "env")
	writeWAVToFile(envNote, "envNote")
	
	
	#note2 = SoundGenerator(waveType = "Square", frequency = 450.0, amplitude = 0.2, duration = 5.0)
	#note3 = SoundGenerator(waveType = "Square", frequency = 600.0, amplitude = 0.2, duration = 5.0)
	#note4 = SoundGenerator(waveType = "Square", frequency = 700.0, amplitude = 0.1, duration = 5.0)
	#note5 = SoundGenerator(waveType = "Square", frequency = 800.0, amplitude = 0.1, duration = 5.0)	
	
	#chord1 = note1 + note2 + note3 + (note4 * 0.5) + note5
	#writeWAVToFile(chord1, "chord1")
	#join1 = sin1 ^  sqr1 ^ sqr2 ^ saw1 ^ chord1
	#mod1 = SoundGenerator(waveType = "Sine", frequency = 2, amplitude = 1.0, duration = 3.0)
	#modjoin1 = 	mod1 ** join1
	#writeWAVToFile(modjoin1, "modjoin1")
	#delay = Delay(delayTime = 100, repetitions = 5, mix = 0.5, decay = 0.0)
	#modjoindelay = delay.generateDelayedSound(modjoin1)
	#writeWAVToFile(modjoindelay, "modjoindelay")
	"""