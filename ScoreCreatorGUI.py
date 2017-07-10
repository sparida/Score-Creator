import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGridLayout, QSlider, QDockWidget, QListWidget, QWidget, QLabel, QFileDialog, QDialog, QDial, QDialogButtonBox
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QMenu, QActionGroup, QGraphicsTextItem, QPushButton, QInputDialog, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import QLineF, QEvent, QRectF
from PyQt5.QtCore import *

from ScoreManager import ScoreManager
from NoteDisplayManager import NoteDisplayManager
from Note import Note
from Effects import Delay
from Envelope import Envelope
from UtilityFunctions import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib as plt
from matplotlib.figure import Figure

class ScoreCreatorGUI(QMainWindow):
    
	def __init__(self):
		super().__init__()
		self.initUI()
             
	def initUI(self):
		# Window Settings Variables
		self.octaveNotes = octave1Notes
		self.cellwidth  = 30
		self.numoctaves = 8
		self.xnum       = 128
		self.ynum   	   = self.numoctaves * 12
		self.xmax       = self.xnum * (self.cellwidth +1)
		self.ymax       = self.ynum * (self.cellwidth +1)
		self.startwidth      = 3
		
		# Music Variables
		self.noteLength = 8
		self.oscType    = "Sine"
		self.wavFile    = "Music"
		self.applyEnvelope = False
		self.envParams   = (200.0, 50.0, 0.5, 200.0)
		self.delayParams = (100.0, 5, 0.5, 0.5)
		
		# Create New Score Manager
		self.sm = ScoreManager()
		self.sm.setEnvelope(Envelope(*self.envParams))
		# Note Display Manager
		self.ndm = NoteDisplayManager(self.cellwidth)

		# Add GUI Elements
		self.addMenuOptions()
		self.addFileMenu()
		self.addEditMenu()
		self.addToolsMenu()
		self.addEnvelopeMenu()
		self.addEffectsMenu()
		self.addSliderDock()
		self.statusBar()
		self.addSceneAndView()

		# Set Geometry
		self.setGeometry(100, 100, 800, 600)
		self.setWindowTitle('Score Creator') 
		
		# Show Window
		self.show()
		
		# Set Window Icon
		self.setWindowIcon(QIcon("Icons/ScoreCreator.png"))
		
		# Misc Inits
		self.handleApplyEnvelope()
		self.handleNoteLengthChange()
		self.view.verticalScrollBar().setValue(1200)
		self.view.horizontalScrollBar().setValue(0)
		
	def addSceneAndView(self):
		self.scene = QGraphicsScene(0,0, self.xmax, self.ymax, self)	
		self.view = QGraphicsView(self.scene, self)		
		self.setCentralWidget(self.view)
		#self.view.setContentsMargins(200, 200, 200, 200)
		self.view.horizontalScrollBar().valueChanged.connect(self.paintGridAndText)
		self.view.verticalScrollBar().valueChanged.connect(self.paintGridAndText)

		self.view.installEventFilter(self)
		self.view.setMouseTracking(True)
		self.paintGridAndText()
		self.view.mousePressEvent = self.handleMousePress
		
		
	def handleMousePress(self, event):
		viewx = event.pos().x()
		viewy = event.pos().y()
		sp = self.view.mapToScene(viewx, viewy)
		indices = self.mapSceneCoordinatesToGrid(sp.x(), sp.y())
		xgrid, ygrid = indices[0], indices[1]
		if(ygrid >= 0):
			if(event.button() == 1):
				noteValue = self.ndm.getNoteFromGridNumber(ygrid)
				velocity = self.sliderVelocity.value() / 100.0
				startLocation = xgrid
				
				note = Note(noteValue, velocity, startLocation, self.noteLength, self.oscType)
				self.sm.addNote(note)
				self.ndm.addNote(xgrid, ygrid, self.noteLength, velocity)
			
			elif(event.button() == 2):
				remInds = self.sm.removeNote(xgrid, self.ndm.getNoteFromGridNumber(ygrid))
				self.ndm.removeNote(remInds)
			self.paintGridAndText()
				
	def mapSceneCoordinatesToGrid(self, x, y):
		note = "C1"
		start = 1
		xgrid = int(x/self.cellwidth) - 3
		ygrid = int(y/self.cellwidth) - 3
		
		if(xgrid < 0 or xgrid > 127):
			return (-1, -1)
		if(ygrid < 0 or ygrid > 94):
			return (-1, -1)
		
		return(xgrid, ygrid)
			
	def paintGrid(self):
		xcurr      = self.startwidth * self.cellwidth
		line = QLineF(xcurr, 0, xcurr, self.ymax - self.cellwidth)
		self.scene.addLine(line, QPen(QBrush(QColor(200, 0, 0, 150)), 3))
		for x in range(self.startwidth + 1, self.xnum+self.startwidth + 1):
			xcurr += self.cellwidth
			line = QLineF(xcurr, 0, xcurr, self.ymax - self.cellwidth)
			self.scene.addLine(line, QPen(QBrush(QColor(0, 20, 240, 150)), 1))

		ycurr      = self.startwidth * (self.cellwidth - 1)
		line = QLineF(0, ycurr, self.xmax - self.cellwidth, ycurr)
		self.scene.addLine(line, QPen(QBrush(QColor(0, 20, 240, 150)), 2))
		for y in range(self.startwidth, self.ynum+self.startwidth - 1):
			ycurr += self.cellwidth
			line = QLineF(0, ycurr, self.xmax - self.cellwidth, ycurr)
			self.scene.addLine(line, QPen(QBrush(QColor(0, 20, 240, 150)), 1))
	
	def paintNotes(self):
		for rects in self.ndm.noteRects:
			rect = QRectF(*rects[0:4])
			vrect = QRectF(*rects[0:2], rects[4], rects[3])
			self.scene.addRect(rect , QPen(QBrush(QColor(0, 200, 0, 200)), 1), QBrush(QColor(0,100, 0, 200)))
			self.scene.addRect(vrect, QPen(QBrush(QColor(0, 200, 0, 200)), 1), QBrush(QColor(0, 255, 0, 200)))
	
	def addTimeLabels(self):
		xcurr      = self.startwidth * self.cellwidth
		textFont = QFont()
		textFont.setBold(True)

		for x in range(1, self.xnum + 1):
			xcurr += self.cellwidth
			yoffset = self.view.mapToScene(0, 0).y()
			xoffset = 0
			if x <= 9:  
				offset = self.cellwidth / 3
			elif x <= 99:  
				offset = self.cellwidth / 4 - self.startwidth
			text = QGraphicsTextItem(str(x - 1 ))
			text.setFont(textFont)
			text.setPos(xcurr + int(xoffset) - self.cellwidth,  yoffset)
			self.scene.addItem(text)
			
	def addNoteLabels(self):
		ycurr = self.startwidth * self.cellwidth
		textFont = QFont()
		textFont.setBold(True)
		
		for y in range( 1, self.ynum):
			ycurr += self.cellwidth
			xoffset = self.view.mapToScene(0, 0).x()
			yoffset = 0
			#print()
			noteName = self.octaveNotes[y%12-1] + str(int(y/12) + 1)
			text = QGraphicsTextItem(noteName)
			text.setFont(textFont)
			text.setPos(xoffset, ycurr + int(yoffset) - self.cellwidth, )
			self.scene.addItem(text)

	def paintGridAndText(self):
		self.scene.clear()
		self.paintGrid()
		self.addTimeLabels()
		self.addNoteLabels()
		self.paintNotes()

		vals = self.getEnvParamsGraph()
		print(vals)
		self.envGraph.ax1.clear()
		self.envGraph.plot(vals = vals)
	
		vals = self.getDelParamsGraph()
		self.delGraph.plot(vals = vals)

		#self.envelopeLabel.setText("Envelope Params:\nAttack: {} ms\nDecay: {} ms\nSustain: {}\nRelease: {} ms\n".format(*self.envParams))
		#self.delayLabel.setText("Delay Params:\nDelay Time: {} ms\nRepetitions: {}\nMix: {}\nDecay: {} ms\n".format(*self.delayParams))
		
	def addMenuOptions(self):
		self.menubar = self.menuBar()

	def addFileMenu(self):
	
		# File Menu Options
		openAction = QAction(QIcon('Icons/Open.png'), 'Open', self)
		openAction.setShortcut('Ctrl+O')
		openAction.setStatusTip('Open Score')
		openAction.triggered.connect(self.handleOpen)
		
		saveAction = QAction(QIcon('Icons/Save.png'), 'Save', self)
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('Save Score')
		saveAction.triggered.connect(self.handleSave)

		wavAction = QAction(QIcon('Icons/Wav.png'), 'WAV File', self)
		wavAction.setShortcut('Ctrl+W')
		wavAction.setStatusTip('Wave File Name')
		wavAction.triggered.connect(self.handleWav)
		
		
		exitAction = QAction(QIcon('Icons/exit.png'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(self.close)
		
		self.fileMenu = self.menubar.addMenu('&File')
		self.fileMenu.addAction(openAction)
		self.fileMenu.addAction(saveAction)
		self.fileMenu.addAction(wavAction)
		self.fileMenu.addAction(exitAction)
		
		self.toolbar = self.addToolBar('Open')
		self.toolbar.addAction(openAction)
		self.toolbar = self.addToolBar('Save')
		self.toolbar.addAction(saveAction)

	def addEditMenu(self):
		self.addNoteLengthMenu()
		self.addOscillatorMenu()
		# Add note length menu as a sub menu to Edit Menu
		self.editMenu = self.menubar.addMenu('&Edit')
		self.editMenu.addMenu(self.noteLengthMenu)
		self.editMenu.addMenu(self.oscillatorMenu)

	def addNoteLengthMenu(self):
	
		# Whole Note Action
		note1Action = QAction(QIcon("Icons/WholeNote.png"), 'Whole Note', self)
		note1Action.setShortcut('Ctrl+1')
		note1Action.setStatusTip('Whole Note : 4 Beats')
		note1Action.triggered.connect(self.handleNoteLengthChange)
		note1Action.setCheckable(True)
		note1Action.setChecked(False)
		note1Action.setData(8)
		# Half Note Action
		note2Action = QAction(QIcon("Icons/HalfNote.png"), 'Half Note', self)
		note2Action.setShortcut('Ctrl+2')
		note2Action.setStatusTip('Half Note : 2 Beats')
		note2Action.triggered.connect(self.handleNoteLengthChange)
		note2Action.setCheckable(True)
		note2Action.setChecked(False)
		note2Action.setData(4)

		# Quarter Note Action
		note3Action = QAction(QIcon("Icons/QuarterNote.png"), 'Quarter Note', self)
		note3Action.setShortcut('Ctrl+3')
		note3Action.setStatusTip('Quarter Note : 1 Beat')
		note3Action.triggered.connect(self.handleNoteLengthChange)
		note3Action.setCheckable(True)
		note3Action.setChecked(True)
		note3Action.setData(2)

		# Eighth Note Action
		note4Action = QAction(QIcon("Icons/EighthNote.png"), 'Eighth Note', self)
		note4Action.setShortcut('Ctrl+4')
		note4Action.setStatusTip('Quarter Note : 4 Beats')
		note4Action.triggered.connect(self.handleNoteLengthChange)
		note4Action.setCheckable(True)
		note4Action.setChecked(False)
		note4Action.setData(1)

		# Create Note Length menu
		self.noteLengthMenu = QMenu("NoteLength")
		self.noteLengthMenu.setIcon(QIcon("Icons/NoteLength.png"))
		# Create Action Group for different Note Lengths
		self.noteActionGroup = QActionGroup(self.noteLengthMenu)
		self.noteActionGroup.setExclusive(True)	

		# Add each note length action to action group and the action group element to the note length menu
		a = self.noteActionGroup.addAction(note1Action)
		self.noteLengthMenu.addAction(a)
		a = self.noteActionGroup.addAction(note2Action)
		self.noteLengthMenu.addAction(a)
		a = self.noteActionGroup.addAction(note3Action)
		self.noteLengthMenu.addAction(a)
		a = self.noteActionGroup.addAction(note4Action)
		self.noteLengthMenu.addAction(a)

		# Add each note length action to the global toolbar
		self.toolbar = self.addToolBar('Whole Note')
		self.toolbar.addAction(note1Action)
		self.toolbar = self.addToolBar('Half Note')
		self.toolbar.addAction(note2Action)
		self.toolbar = self.addToolBar('Quarter Note')
		self.toolbar.addAction(note3Action)
		self.toolbar = self.addToolBar('Eighth Note')
		self.toolbar.addAction(note4Action)
		
	def addOscillatorMenu(self):
	
		# Sine Wave
		sineAction = QAction(QIcon("Icons/Sine.png"), 'Sine', self)
		sineAction.setShortcut('Alt+1')
		sineAction.setStatusTip('Sine Wave')
		sineAction.triggered.connect(self.handleOscillatorChange)
		sineAction.setCheckable(True)
		sineAction.setChecked(True)
		sineAction.setData("Sine")

		# Sine Wave
		squareAction = QAction(QIcon("Icons/Square.png"), 'Square', self)
		squareAction.setShortcut('Alt+2')
		squareAction.setStatusTip('Square Wave')
		squareAction.triggered.connect(self.handleOscillatorChange)
		squareAction.setCheckable(True)
		squareAction.setChecked(False)
		squareAction.setData("Square")

		# Sine Wave
		sawAction = QAction(QIcon("Icons/Sawtooth.png"), 'Sawtooth', self)
		sawAction.setShortcut('Alt+3')
		sawAction.setStatusTip('Sawtooth Wave')
		sawAction.triggered.connect(self.handleOscillatorChange)
		sawAction.setCheckable(True)
		sawAction.setChecked(False)
		sawAction.setData("Sawtooth")

		# Create oscilattor menu
		self.oscillatorMenu = QMenu("Oscillator")
		self.oscillatorMenu.setIcon(QIcon("Icons/Osc.png"))
		# Create Action Group for different Note Lengths
		self.oscillatorGroup = QActionGroup(self.oscillatorMenu)
		self.oscillatorGroup.setExclusive(True)	

		# Add each note length action to action group and teh action group element to the note length menu
		a = self.oscillatorGroup.addAction(sineAction)
		self.oscillatorMenu.addAction(a)
		a = self.oscillatorGroup.addAction(squareAction)
		self.oscillatorMenu.addAction(a)
		a = self.oscillatorGroup.addAction(sawAction)
		self.oscillatorMenu.addAction(a)


		# Add each note length action to the global toolbar
		self.toolbar = self.addToolBar('Sine Wave')
		self.toolbar.addAction(sineAction)
		self.toolbar = self.addToolBar('Square Wave')
		self.toolbar.addAction(squareAction)
		self.toolbar = self.addToolBar('Sawtooth Wave')
		self.toolbar.addAction(sawAction)

	def addEnvelopeMenu(self):
	
		# File Menu Options
		self.applyEnvelopeAction = QAction(QIcon("Icons/adsr.png"), 'Apply Envelope', self)
		self.applyEnvelopeAction.setShortcut('Ctrl+V')
		self.applyEnvelopeAction.setStatusTip('Apply Envelope to Notes')
		self.applyEnvelopeAction.toggled.connect(self.handleApplyEnvelope)
		self.applyEnvelopeAction.setCheckable(True)
		self.applyEnvelopeAction.setChecked(False)
		
		envPrefAction = QAction(QIcon("Icons/Settings.png"), 'Envelope Preferences', self)
		envPrefAction.setShortcut('Alt+V')
		envPrefAction.setStatusTip('Edit Envelope Type')
		envPrefAction.triggered.connect(self.handleEnvelope)		
		
		
		self.envMenu = self.menubar.addMenu('&Envelope')
		self.envMenu.addAction(self.applyEnvelopeAction)
		self.envMenu.addAction(envPrefAction)

		self.toolbar = self.addToolBar('Apply Envelope')
		self.toolbar.addAction(self.applyEnvelopeAction)

	def addToolsMenu(self):
		clearAction = QAction(QIcon('Icons/Clear.png'), 'Clear Score', self)
		clearAction.setShortcut('Ctrl+C')
		clearAction.setStatusTip('Clear Score')
		clearAction.triggered.connect(self.handleClearScore)

		genAction = QAction(QIcon('Icons/Gen.png'), 'Generate', self)
		genAction.setShortcut('Ctrl+G')
		genAction.setStatusTip('Generate Music')
		genAction.triggered.connect(self.handleGen)
		
		self.fileMenu = self.menubar.addMenu('&Tools')
		self.fileMenu.addAction(clearAction)
		self.fileMenu.addAction(genAction)
		
		self.toolbar = self.addToolBar('Clear Score')
		self.toolbar.addAction(clearAction)
		self.toolbar = self.addToolBar('Generate')
		self.toolbar.addAction(genAction)
		
	def addEffectsMenu(self):
		self.addDelayMenu()
		
		# Effects Menu Options
		self.applyEffectsAction = QAction(QIcon("Icons/effects.png"), 'Apply Effects', self)
		self.applyEffectsAction.setShortcut('Ctrl+E')
		self.applyEffectsAction.setStatusTip('Apply Effects to Notes')
		self.applyEffectsAction.toggled.connect(self.handleApplyEffects)
		self.applyEffectsAction.setCheckable(True)
		self.applyEffectsAction.setChecked(True)
		
		self.effectsMenu = QMenu('Effects')
		self.effectsMenu.addAction(self.applyEffectsAction)
		self.effectsMenu.addMenu(self.delayMenu)
		
		self.menubar.addMenu(self.effectsMenu)
		
		self.toolbar = self.addToolBar('Apply Effects')
		self.toolbar.addAction(self.applyEffectsAction)

	def addDelayMenu(self):
	
		# File Menu Options
		self.applyDelayAction = QAction(QIcon(), 'Apply Delay', self)
		self.applyDelayAction.setShortcut('Ctrl+D')
		self.applyDelayAction.setStatusTip('Apply Delay to Notes')
		self.applyDelayAction.toggled.connect(self.handleApplyDelay)
		self.applyDelayAction.setCheckable(True)
		self.applyDelayAction.setChecked(True)
		
		delayPrefAction = QAction(QIcon("Icons/Settings.png"), 'Delay Preferences', self)
		delayPrefAction.setShortcut('Alt+D')
		delayPrefAction.setStatusTip('Edit Delay Settings')
		delayPrefAction.triggered.connect(self.handleDelay)		
		
		
		self.delayMenu = QMenu('Delay')
		self.delayMenu.setIcon(QIcon("Icons/Delay.png"))
		self.delayMenu.addAction(self.applyDelayAction)
		self.delayMenu.addAction(delayPrefAction)
	
	def addSliderDock(self):
		self.sliderTempo = QSlider(1)
		self.sliderTempo.setTickInterval(1)
		self.sliderTempo.setTickPosition(1)
		self.sliderTempo.setRange(50, 300)
		self.tempoLabel = QLabel("Tempo:" + str(self.sliderTempo.value()))
		self.tempoLabel.setAlignment(Qt.AlignCenter)
		self.sliderTempo.valueChanged.connect(self.handleTempoChange)
		self.sliderTempo.setValue(100)
		
		self.sliderVelocity = QSlider(1)
		self.sliderVelocity.setTickInterval(1)
		self.sliderVelocity.setTickPosition(1)
		self.sliderVelocity.setRange(0, 100)
		self.velocityLabel = QLabel("Note Velocity:"  + str(self.sliderVelocity.value()))
		self.velocityLabel.setAlignment(Qt.AlignCenter)
		self.sliderVelocity.valueChanged.connect(self.handleVelocityChange)
		self.sliderVelocity.setValue(20)
		
		#self.envelopeLabel = QLabel("Envelope:"  + str(self.envParams))
		self.envelopeLabel = QLabel("\n\n" + "ADSR Curve")
		self.envelopeLabel.setAlignment(Qt.AlignCenter)

		#self.delayLabel = QLabel("Delay:"  + str(self.delayParams))
		self.delayLabel = QLabel("\n\n" + "Delay Representation")
		self.delayLabel.setAlignment(Qt.AlignCenter)
		
		self.envGraph = MyCanvas(5, 6, 100)
		vals = self.getEnvParamsGraph()
		self.envGraph.plot(vals = vals)
		
		self.delGraph = MyCanvas(5, 6, 100)
		self.delGraph.plot(vals)
		
		self.docklayout = QGridLayout()
		self.docklayout.addWidget(self.sliderTempo, 0, 0)
		self.docklayout.addWidget(self.sliderVelocity, 0, 1)
		self.docklayout.addWidget(self.tempoLabel, 1, 0)
		self.docklayout.addWidget(self.velocityLabel, 1, 1)
		self.docklayout.addWidget(self.envelopeLabel, 2, 0)
		self.docklayout.addWidget(self.delayLabel, 2, 1)
		self.docklayout.addWidget(self.envGraph, 3, 0)
		self.docklayout.addWidget(self.delGraph, 3, 1)
		
		self.dockWidgets = QWidget()
		self.dock = QDockWidget()
		
		self.dockWidgets.setLayout(self.docklayout)
		self.dock.setWidget(self.dockWidgets)
		self.addDockWidget(8, self.dock)

	def getEnvParamsGraph(self):
		x = []

		x_sum = 0
		x.append(x_sum)

		x_sum += self.envParams[0]
		x.append(x_sum)

		x_sum += self.envParams[1]
		x.append(x_sum)
		
		x_sum += x_sum
		x.append(x_sum)

		x_sum += self.envParams[3]
		x.append(x_sum)
		
		y = [0.0, 1.0, self.envParams[2], self.envParams[2], 0.0]
		
		return (x, y)

	def getDelParamsGraph(self):
		return ([0, 0], [1, 2])
	def handleOpen(self):
		fname = QFileDialog.getOpenFileName(self, "Open Score")[0]
		#self.handleClearScore()
		if len(fname) >= 1:
			self.sm.readScore(fname)
			self.ndm.addNotesFromScoreManager(self.sm.notes)
			self.paintGridAndText()
		
	def handleSave(self):
		fname = QFileDialog.getSaveFileName(self, "Save Score")[0]
		if len(fname) >= 1:
			self.sm.writeScore(fname)

	def handleWav(self):
		fname, ok = QInputDialog.getText(self, 'WAV File Name', 'Enter file name for final generated music:')
		
	def handleNoteLengthChange(self):
		self.noteLength = int(self.noteActionGroup.checkedAction().data())
		
	def handleOscillatorChange(self):
		self.oscType = str(self.oscillatorGroup.checkedAction().data())	
		
	def handleClearScore(self):
		self.sm.clear()
		self.ndm.clear()
		self.paintGridAndText()
		
	def handleGen(self):
		self.statusBar().clearMessage()
		self.statusBar().showMessage("Initializing Envelope")
		self.sm.setEnvelope(Envelope(*self.envParams))
		self.statusBar().clearMessage()
		self.statusBar().showMessage("Initializing Envelope")
		#print("Writing music score to " + str(self.wavFile) + "Score.txt")
		self.sm.writeScore(str(self.wavFile) + "Score.txt")
		self.statusBar().clearMessage()
		self.statusBar().showMessage("Generating Sound")
		#print("Generating Sound")
		self.sm.setTempo(int(self.sliderTempo.value()))
		soundObj = self.sm.generateSound()
		if self.applyEffectsAction.isChecked():
			#print("Applying Effects")
			self.statusBar().clearMessage()
			self.statusBar().showMessage("Applying Effects")

			if self.applyDelayAction.isChecked():
				#print("Applying Delay")
				self.statusBar().clearMessage()
				self.statusBar().showMessage("Applying Delay")

				delay = Delay(*self.delayParams)
				soundObj = delay.generateDelayedSound(soundObj)


		self.statusBar().clearMessage()
		self.statusBar().showMessage("Writing WAV file to " + self.wavFile)
	
		#print("Writing WAV file to " + self.wavFile)
		writeWAVToFile(soundObj, self.wavFile)
		self.statusBar().clearMessage()
		self.statusBar().showMessage("Music Generation Complete")
		
	def handleApplyEnvelope(self):
		self.sm.setApplyEnvelope(self.applyEnvelopeAction.isChecked())
		
	def handleEnvelope(self):
		params = []
		params.append( Parameter("Attack" , "ms" , 10 ,  3000 , 5 , self.envParams[0]))
		params.append( Parameter("Decay"  , "ms" , 10 ,  3000 , 5 , self.envParams[1]))
		params.append( Parameter("Sustain", ""   ,  0 ,   20  , 1 , int(self.envParams[2]*20)))
		params.append( Parameter("Release", "ms" , 10 ,  3000 , 5 , self.envParams[3]))
		dialog = ParamDialog(params = params, name = "Envelope Parameters", icon = QIcon("Icons/adsr.png"))
		retparams, ok = dialog.getParameters()
		if ok:
			self.envParams = (retparams[0], retparams[1], retparams[2]/20.0, retparams[3])
			self.paintGridAndText()

	def handleApplyEffects(self):
		pass

	def handleApplyDelay(self):
		pass

	def handleDelay(self):
		params = []
		params.append( Parameter("Delay Time" , "ms", 10, 1000, 5,     self.delayParams[0]))
		params.append( Parameter("Repeats"    , ""  ,  1,   20, 1,     self.delayParams[1]))
		params.append( Parameter("Mix"        , ""  ,  0,   20, 1, int(self.delayParams[2]*20)))
		params.append( Parameter("Decay"      , ""  ,  0,   20, 1, int(self.delayParams[3]*20)))
		dialog = ParamDialog(params = params, name = "Delay Parameters", icon = QIcon("Icons/Delay.png"))
		retparams, ok = dialog.getParameters()
		if ok:
			self.delayParams = (retparams[0], retparams[1], retparams[2]/20.0, retparams[3]/20.0)
			self.paintGridAndText()

	def handleTempoChange(self):
		self.tempoLabel.setText("Tempo:" + str(self.sliderTempo.value()))

	def handleVelocityChange(self):
		self.velocityLabel.setText("Note Velocity:" + str(self.sliderVelocity.value() / 100.0))
		
class Parameter():
	def __init__(self, label, units, min, max, step, default):
		self.label   = label
		self.min     = min
		self.max     = max
		self.units   = units
		self.step    = step
		self.default = default

class ParamDialog(QDialog):
	def __init__(self, parent = None, params = [], name = "Dialog", icon = QIcon()):
		super(ParamDialog, self).__init__(parent)
		self.layout = QGridLayout()
		self.vblayout = QVBoxLayout(self)
		self.params = params
		self.knobs = []
		self.name = name
		self.icon = icon
		self.setWindowTitle(self.name)
		self.initUI()

		
	def initUI(self):

		for i in range(len(self.params)):
			param = self.params[i]
			knob = QDial()
			knob.setRange(param.min, param.max)
			knob.setSingleStep(param.step)
			knob.valueChanged.connect(self.handleKnob)
			knob.setWrapping(False)
			knob.setNotchesVisible(True)
			
			knobNameLabel  = QLabel(param.label)
			knobNameLabel.setAlignment(Qt.AlignCenter)
			knobValueLabel = QLabel(str(knob.value())  + " " + param.units)
			knobValueLabel.setAlignment(Qt.AlignCenter)
			self.layout.addWidget(knobValueLabel, 0, i)
			self.layout.addWidget(knob, 1, i)
			self.layout.addWidget(knobNameLabel , 2, i)
			
			self.knobs.append((knob, knobNameLabel, knobValueLabel))
			knob.setValue(param.default)
		
		self.buttonBox = QDialogButtonBox()
		self.buttonBox.setOrientation(Qt.Horizontal)
		self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		self.vblayout.addLayout(self.layout)
		self.vblayout.addWidget(self.buttonBox)
		self.setWindowIcon(self.icon)
			
	def getReturnValues(self):
		return [self.knobs[i][0].value() for i in range(len(self.knobs))]
		
	def handleKnob(self):
		sender = self.sender()
		for i in range(len(self.knobs)):
			knob, name, value = self.knobs[i]
			param = self.params[i]
			if knob is sender:
				value.setText(str(knob.value())  + " " + param.units)

	def getParameters(self):
		ok = self.exec_()
		return (tuple(self.getReturnValues()), ok)

		import random

class MyCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = plt.figure.Figure(figsize=(width, height), dpi=dpi)   
		self.fig.set_tight_layout('tight')
		super(MyCanvas, self).__init__(self.fig)
	def plot(self, parent=None, vals = ([1, 2, 3, 4], [1, 2, 3, 4])):
		self.ax1 = self.figure.add_subplot(111)
		self.ax1.plot(vals[0],vals[1], 'r-')

		
if __name__ == '__main__':
    
	app = QApplication(sys.argv)
	sc = ScoreCreatorGUI()
	#main = MyCanvas(5, 6, 100)
	#main.mystatic()
	#main.show()
	sys.exit(app.exec_())