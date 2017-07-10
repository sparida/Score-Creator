import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd

from SoundGenerator import SoundGenerator
from Note import Note
from UtilityFunctions import *
from Effects import Delay

# Handle generaton of ADSR Envelope Object (Type: SoundGenerator)
class Envelope():
	# Initialize values for A(msec), D(msec), S(0-1) and R(msec)
	def __init__(self, attack = 1000.0, decay = 200.0, sustain = 0.5, release = 400):
		self.attack  = float(attack)
		self.decay   = float(decay)
		self.sustain = float(sustain)
		self.release = float(release)
		
	# Obtain the ADSR Enevelope to shape note sound from the envelope object
	# Note that the ADSR envelope object is just a regular Sound Generator Object
	# With the A, D, S and R parts joined together as a single wave in the sound array
	def getADSREnvelope(self, soundObj):
		sampleCount = len(soundObj.getSound())
		
		adsr = np.array([])
		# Handle Attack
		if (sampleCount > 0):
			attackEnvelope  = self.getLinearEnvelope(0.0, 1.0, self.attack)
			attackCount = len(attackEnvelope)
			if(attackCount > sampleCount):
				attackEnvelope = attackEnvelope[:sampleCount]
			sampleCount = sampleCount - attackCount
			adsr = np.append(adsr, attackEnvelope)

		# Handle Decay
		if (sampleCount > 0):
			decayEnvelope  = self.getLinearEnvelope(1.0, self.sustain, self.decay)
			decayCount = len(decayEnvelope)
			if(decayCount > sampleCount):
				decayEnvelope = decayEnvelope[:sampleCount]
			sampleCount = sampleCount - decayCount
			adsr = np.append(adsr, decayEnvelope)

		
		# Handle Sustain
		if(sampleCount > 0):
			sustainEnvelope = self.getLinearEnvelope(self.sustain, self.sustain, sampleCount * 1000.0 /SAMPLE_RATE )
			adsr = np.append(adsr, sustainEnvelope)
			sampleCount = sampleCount - len(sustainEnvelope)

		# Handle Release
		releaseEnvelope = self.getLinearEnvelope(self.sustain, 0.0, self.release)
		adsr = np.append(adsr, releaseEnvelope)
	
		# Create ADSR Envelope
		adsrDuration = len(adsr) * 1.0 / SAMPLE_RATE
		#print(adsrDuration)
		adsrEnvelopeObject = SoundGenerator("ADSR", 1.0/adsrDuration, np.max(adsr), adsrDuration)
		adsrEnvelopeObject.setSound(adsr)
		return adsrEnvelopeObject
	
	# Given the start amplotude, the stop amplitude and the duration of the wave
	# Generates  a sampled linear wave as a SoundGenerator sound array (numpy array)
	# Used to create A, D, S and R and part of teh ADSR Envelope
	def getLinearEnvelope(self, start, stop, duration):
		timeInSeconds = duration / 1000.0
		# Number of smaples needed
		sampleCount =  convertTimeToSampleCount(duration)
		
		timeArray = np.linspace(0, timeInSeconds, num = sampleCount)
		
		slope = (stop - start) / timeInSeconds
		#print(slope)
		linearCalculator = np.vectorize(lambda t: slope*t + start)
		#print (linearCalculator(timeArray))
		return linearCalculator(timeArray)