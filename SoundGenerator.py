import numpy as np
from scipy.io.wavfile import write
from math import pi, sin, floor
from fractions import gcd
from UtilityFunctions import *
class SoundGenerator():
	
	# Constants
	def __init__(self, waveType = "Sine", frequency = 500, amplitude = 1.0, duration = 5):
	
			# Initialize Internal Variables
			self.waveType  = str(waveType)
			self.frequency = float(frequency)
			self.amplitude = limitAmplitude(amplitude)			
			self.duration  = float(duration)
			self.sampleCount = self.getSampleCount()
			self.sound     = np.array([])
			self.limit     = np.vectorize(limitAmplitude)

			# Generate Sound
			if  (waveType == "Sine"):
				self.sound = self.generateSineWave()
			elif(waveType == "Square"):
				self.sound = self.generateSquareWave()
			elif(waveType == "Sawtooth"):
				self.sound = self.generateSawtoothWave()
			elif(waveType == "Constant"):
				self.sound = self.generateConstantWave()
			elif(waveType == "Noise"):
				self.sound = self.generateWhiteNoiseWave()
			elif(waveType == "Combination"):
				self.sound = self.sound

	def getSampleCount(self):
		return int(self.duration * SAMPLE_RATE)	
		pass
	
	def getSinglePhaseArray(self):
		singleCycleLength = SAMPLE_RATE / float(self.frequency)
		omega = pi * 2 / singleCycleLength
		phaseArray = np.arange(0, int(singleCycleLength)) * omega
		return phaseArray
		
	def generateSineWave(self):
		# Get Phase Array		
		phaseArray = self.getSinglePhaseArray()
		# Compute Sine Values and scale by amplitude
		singleCycle = self.amplitude * np.sin(phaseArray)
		# Resize to match duration
		return np.resize(singleCycle, (self.sampleCount,)).astype(np.float)	
		
	def generateSquareWave(self):
		# Use the fact that sign of sine is square wave and scale by amplitude
		return self.amplitude * np.sign(self.generateSineWave())
		
	def generateSawtoothWave(self):
		# Get Phase Array		
		phaseArray = self.getSinglePhaseArray()
		# Compute Saw Values and scale by amplitude
		piInverse = 1/pi
		saw = np.vectorize(lambda x: 1 - piInverse*x) 
		singleCycle =  self.amplitude * saw(phaseArray)
		# Resize to match duration
		return np.resize(singleCycle, (self.sampleCount,)).astype(np.float)	

	def generateConstantWave(self):
		# Get Phase Array		
		phaseArray = self.getSinglePhaseArray()
		# Assign to amplitude
		singleCycle = self.amplitude
		# Resize to match duration
		return np.resize(singleCycle, (self.sampleCount,)).astype(np.float)	
		
	def generateWhiteNoiseWave(self):
		# Random samples between -1 and 1
		return np.random.uniform(-1, 1, self.getSampleCount()) 

	def combineSounds(self, soundObj, operator = '+'):
		# Figure out which is the longer sound
		if len(self.sound) < len(soundObj.getSound()):
			minSound = np.copy(self.getSound())
			maxSound = np.copy(soundObj.getSound())
		else:
			maxSound = np.copy(self.getSound())
			minSound = np.copy(soundObj.getSound())
		
		# Perform appropriate operation
		if operator == '+':	
			maxSound[0:len(minSound)] = maxSound[0:len(minSound)] + minSound
		elif operator == '-':	
			maxSound[0:len(minSound)] = maxSound[0:len(minSound)] - minSound
		elif operator == '*':	
			maxSound[0:len(minSound)] = maxSound[0:len(minSound)] * minSound

		# Limite sound values to within -1 and +1
		newSound = self.limit(maxSound)
			
		# Calculate metadata for new sound
		newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
		newDuration = float(len(newSound)) / SAMPLE_RATE
		newAmplitude = np.max(newSound)
			
		# Create new sound object and return object
		returnObj = SoundGenerator(waveType = "Combination", frequency = newFrequency, amplitude = newAmplitude, duration = newDuration)

		# Set sound value to newSound
		returnObj.setSound(newSound)
		return returnObj		
		
	def __add__(self, soundObj):
		return self.combineSounds(soundObj, '+')
			
	def __sub__(self, soundObj):
		return self.combineSounds(soundObj, '-')

	def __mul__(self, soundObj):
		if isinstance(soundObj, int) or isinstance(soundObj, float):
			scaleFactor = limitAmplitude(soundObj)
			if(scaleFactor < 0):
				scaleFactor = 0.0
			returnObj = SoundGenerator(self.waveType, self.frequency, self.amplitude * scaleFactor, self.duration)
			sound = self.getSound()
			returnObj.setSound(sound * scaleFactor)
			return returnObj
		return self.combineSounds(soundObj, '*')
	
	def __xor__(self, soundObj):
		
		# Join two sound pieces together
		newSound = np.append(self.getSound(), soundObj.getSound())
			
		# Calculate metadata for new sound
		newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
		newDuration = self.getDuration() + soundObj.getDuration()
		newAmplitude = np.max(newSound)
			
		# Create new sound object and return object
		returnObj = SoundGenerator(waveType = "Join", frequency = newFrequency, amplitude = newAmplitude, duration = newDuration)

		# Set sound value to newSound
		returnObj.setSound(newSound)
		return returnObj
		
	def __pow__(self, soundObj):
		# Figure out which is the longer sound
		if len(self.sound) < len(soundObj.getSound()):
			minSound = np.copy(self.getSound())
			maxSound = np.copy(soundObj.getSound())
			
		else:
			maxSound = np.copy(self.getSound())
			minSound = np.copy(soundObj.getSound())
		minSound = np.resize(minSound, (len(maxSound),))
		#newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
		newDuration = float(len(maxSound))/SAMPLE_RATE
		# Frequency does not matter here
		minSoundObj = SoundGenerator(waveType = "Temp", frequency = 100, amplitude = np.max(minSound), duration = newDuration)
		minSoundObj.setSound(minSound)
		maxSoundObj = SoundGenerator(waveType = "Temp", frequency = 100, amplitude = np.max(maxSound), duration = newDuration)
		maxSoundObj.setSound(maxSound)
		return (minSoundObj * maxSoundObj)

	def __str__(self):
		return "WT: " + self.waveType + " F: " + str(self.frequency) + " A: " + str(self.amplitude) + " D: " + str(self.duration)

	def getSound(self):
		return self.sound

	def setSound(self, soundArray):
		self.sound = soundArray

	def getFrequency(self):
		return self.frequency

	def getDuration(self):
		return self.duration
		
	def shiftBy(self, numberOfSamples):
		sound = self.getSound()
		sound = np.roll(sound, numberOfSamples)
		sound = np.append(np.zeros(numberOfSamples), sound[numberOfSamples:])
		retSoundObj = SoundGenerator(self.waveType, self.frequency, self.amplitude, self.duration)
		retSoundObj.setSound(sound)
		return retSoundObj
if __name__ == "__main__":
	sin1 = SoundGenerator(waveType = "Sine"  , duration = 3.0)
	sqr1 = SoundGenerator(waveType = "Square", frequency = 400.0, amplitude = 0.2, duration = 3.0)
	sqr2 = SoundGenerator(waveType = "Square", frequency = 500.0, amplitude = 0.2, duration = 3.0)
	saw1 = SoundGenerator(waveType = "Sawtooth"  , duration = 3)
	
	note1 = SoundGenerator(waveType = "Square", frequency = 400.0, amplitude = 0.2, duration = 5.0)
	note2 = SoundGenerator(waveType = "Square", frequency = 450.0, amplitude = 0.2, duration = 5.0)
	note3 = SoundGenerator(waveType = "Square", frequency = 600.0, amplitude = 0.2, duration = 5.0)
	note4 = SoundGenerator(waveType = "Square", frequency = 700.0, amplitude = 0.1, duration = 5.0)
	note5 = SoundGenerator(waveType = "Square", frequency = 800.0, amplitude = 0.1, duration = 5.0)	
	
	chord1 = note1 + note2 + note3 + (note4 * 0.5) + note5

	join1 = sin1 ^  sqr1 ^ sqr2 ^ saw1 ^ chord1
	mod1 = SoundGenerator(waveType = "Square", frequency = 3.0, amplitude = 1.0, duration = 3.0)
	modjoin1 = 	mod1 ** join1
	writeWAVToFile(modjoin1, "modjoin1")

