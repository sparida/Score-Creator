import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd

from SoundGenerator import SoundGenerator
from UtilityFunctions import *

# Implements a delay effect
# Delay time  - Delay in msecs between each different delay 
# repetitions - Total number of additonal delays
# mix         - Weight given to original signal vs delay signal
#decay        - Controls the attrituion of  repetition volume in time (1.0: Full Attrition , 0.0: No Attrition )
class Delay():
	def __init__(self, delayTime = 1000.0, repetitions = 3, mix = 1.0, decay = 1.0):
		self.repetitions = min(repetitions, 10)
		self.delayTime   = float(delayTime)
		self.mix = mix
		self.delayInSampleCount = convertTimeToSampleCount(self.delayTime)
		self.decay = float(max(limitAmplitude(decay), 0.0))
		
		
	def generateDelayedSound(self, soundObj):
		
		# Initial black sound for delayed sound
		delayedSound  = SoundGenerator(waveType = "Constant", frequency = 5, amplitude = 0.0, duration = soundObj.getDuration())
		# Initial black sound for delayed sound
		originalSound = SoundGenerator(waveType = "Constant", frequency = 5, amplitude = 0.0, duration = soundObj.getDuration())
		# Copy into new variable to avoid accidental modification of original sound
		originalSound.setSound(np.copy(soundObj.getSound()))
		
		# Decay coefficents(weigths) for each repetition of decay
		# (If decay = 0, they are all the same
		# (If decay = 1, they are samples of linearly decreasing curve from 1.0 to 0.0)
		decayCoeffs = np.linspace(1.0, (1 - self.decay), self.repetitions + 1)[1:]
		
		# For each repetition
		for r in range(1, self.repetitions + 1):
			# Create copy of original sound
			originalSoundCopy = SoundGenerator(waveType = "Constant", frequency = 5, amplitude = 0.0, duration = soundObj.getDuration())
			originalSoundCopy.setSound(np.copy(soundObj.getSound()))
			
			# Genrate sound shifted by delayTime * repetition number
			individualDelay = originalSoundCopy.shiftBy(self.delayInSampleCount * r)
			
			# Superimpose with existing delay sound
			delayedSound = delayedSound  + (individualDelay * decayCoeffs[r - 1])
		
		# Return weighted average of orginal sound and delayed sound based on mix value
		return (originalSound * (1-self.mix)) + (delayedSound * self.mix)
		
