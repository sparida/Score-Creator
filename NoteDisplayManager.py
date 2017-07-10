from UtilityFunctions import *

class NoteDisplayManager():
	def __init__(self, cellwidth = 30):
		self.cellwidth = cellwidth

		# Create Cell Occupied Set:
		self.occupiedCells = set()
		self.noteRects = []
	
	def removeNote(self, removeIndices):
		self.noteRects = [self.noteRects[i] for i in range(len(self.noteRects)) if i not in removeIndices]
		
	def addNote(self, xgrid, ygrid, noteLength, velocity):
		self.addOccupiedCells(xgrid, ygrid, noteLength)
		self.addNoteRect(xgrid, ygrid, noteLength, velocity)
		
	def addNotesFromScoreManager(self, notes):
		for note in notes:
			print(note.noteValue)
			xgrid, ygrid = self.mapFromScoreToGrid(note.noteValue, note.startLocation)
			self.addNoteRect(xgrid, ygrid, note.noteLength, note.velocity)
		
	def mapFromScoreToGrid(self, noteValue, startLocation):
		xgrid = startLocation
		ygrid = 12 * (int(noteValue[-1]) - 1) + octave1Notes.index(noteValue[:-1])
		if (ygrid %12 == 11):
			ygrid -= 12
		return (xgrid, ygrid)
		
		
	def addNoteRect(self, xgrid, ygrid, noteLength, velocity):
		x = (xgrid + 3) * self.cellwidth + 5
		y = (ygrid + 3) * self.cellwidth 
		w = noteLength  * self.cellwidth - 10
		h = self.cellwidth - 5
		self.noteRects.append((x, y, w, h, velocity*w))
		
	def isCellOccupied(self, xgrid, ygrid):
		cell = str(xgrid) + "|" + str(ygrid)
		return (cell in self.occupiedCells)
		
	def addOccupiedCells(self, xgrid, ygrid, noteLength):
		for i in range(noteLength):
				cell = str(xgrid + i) + "|" + str(ygrid)
				self.occupiedCells.add(cell)
				
	def removeOccupiedCells(self, xgrid, ygrid, noteLength):
		for i in range(noteLength):
				cell = str(xgrid) + "|" + str(grid + i)
				self.occupiedCells.remove(cell)
				
	def getNoteFromGridNumber(self, ygrid):
		noteChar = octave1Notes[ygrid % 12]
		octave   = int(ygrid/12) + 1
		if(noteChar == "B"):
			octave += 1
		return (str(noteChar) + str(octave))
		
	def clear(self):
		self.occupiedCells = set()
		self.noteRects = []