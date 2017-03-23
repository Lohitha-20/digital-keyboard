from PyQt5.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsView, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsTextItem, QVBoxLayout, QPushButton, QSpacerItem, QInputDialog
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QKeySequence, QColor

import constants
from keyboard import Keyboard

class PianoKeyItem(QGraphicsRectItem):
    def mousePressEvent(self, event):
        if hasattr(self, 'note') and self.note is not None:
            mapping_notes = self.instrument_widget.keyboard.mapping_notes
            if not self.note in mapping_notes:
                mapping_notes.append(self.note)
            else:
                mapping_notes.remove(self.note)
            self.instrument_widget.updateUI()

class DigitalInstrumentWidget(QGraphicsView):

    def __init__(self):
        super(DigitalInstrumentWidget, self).__init__()

        self.keyboard = Keyboard()
        self.initUI()

    def createButton(self, text, event):
        button = QPushButton()
        button.setText(text)
        button.show()
        button.clicked.connect(event)
        self.layout.addWidget(button, 100, Qt.AlignCenter)

    def initButtons(self):
        self.layout = QVBoxLayout()

        button_text_events = [
            ('Set Keyboard Type', self.keyboardTypeButtonEvent),
            ('Reset Mappings', self.resetButtonEvent),
            ('Save Mappings', self.saveButtonEvent),
            ('Load Mappings', self.loadButtonEvent),
            ('Delete Mappings', self.deleteButtonEvent),
        ]

        for text, event in button_text_events:
            self.createButton(text, event)

        self.layout.addSpacerItem(QSpacerItem(100, 500))
        self.setLayout(self.layout)

    def createTextItem(self, scene, text, x, y):
        text_item = QGraphicsTextItem(text)
        text_item.setZValue(100)
        text_item.setPos(x, y)
        text_item.adjustSize()
        scene.addItem(text_item)
        return text_item

    def initText(self, scene):
        self.chordMappings = self.createTextItem(
                scene, "Key Mappings:" + '\n' + "None", 0, -300)
        self.octaveLeft = self.createTextItem(
                scene, "Octave: " + str(self.keyboard.octave), 150, -30)
        self.octaveRight = self.createTextItem(
                scene, "Octave: " + str(self.keyboard.octave + 1), 475, -30)

    def drawWhiteKey(self, i):
        key = PianoKeyItem(
            self.keyAreaBounds.x() + i * self.whiteKeyWidth,
            self.keyAreaBounds.y(),
            self.whiteKeyWidth,
            self.keyAreaBounds.height()
        )
        key.setBrush(Qt.white)
        key.mappingLabel = QGraphicsTextItem()
        key.mappingLabel.setDefaultTextColor(Qt.black)
        return key

    def drawBlackKey(self, i):
        startX = self.keyAreaBounds.x() + 2 * i * self.blackKeyWidth + self.blackKeyWidth * 1.5
        if i > 6:
            startX += 3*self.whiteKeyWidth
        elif i > 4:
            startX += 2*self.whiteKeyWidth
        elif i > 1:
            startX += self.whiteKeyWidth

        key = PianoKeyItem(
            startX,
            self.keyAreaBounds.y(),
            self.blackKeyWidth,
            self.keyAreaBounds.height() * 0.6
        )
        key.setBrush(Qt.black)
        key.mappingLabel = QGraphicsTextItem()
        key.mappingLabel.setDefaultTextColor(Qt.white)
        return key

    def drawKeys(self, scene, keyIndices, drawKeyFunction):
        keyAreaBounds = QRect(0, 0, self.size().width() * .85, self.size().height() * 0.4)
        keys = []
        for i in range(len(keyIndices)):
            key = drawKeyFunction(i)
            key.instrument_widget = self
            key.note = constants.DiscreteNotes(keyIndices[i])

            key.mappingLabel.setZValue(100)
            key.mappingLabel.setPlainText('A')
            key.mappingLabel.setPos(
                key.boundingRect().x() + key.boundingRect().width()/2 - key.mappingLabel.boundingRect().width()/2,
                key.boundingRect().y() + key.boundingRect().height()*0.8
            )

            scene.addItem(key.mappingLabel)
            scene.addItem(key)
            keys.append(key)
        return keys
        
    def initUI(self):
        windowWidth = 800
        windowHeight = 500
        self.resize(windowWidth, windowHeight)
        self.move(100, 100)
        self.setWindowTitle('Digital Keyboard')
        self.show()

        # Set up graphics stuff
        scene = QGraphicsScene()

        self.initButtons()
        self.initText(scene)
        
        self.keyAreaBounds = QRect(0, 0, windowWidth * .85, windowHeight * 0.4)
        self.whiteKeyWidth = self.keyAreaBounds.width() / 14
        self.whiteKeyIndices = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 22]
        self.whiteKeys = self.drawKeys(scene, self.whiteKeyIndices, self.drawWhiteKey)

        self.blackKeyWidth = self.whiteKeyWidth / 2
        self.blackKeyIndices = [1, 3, 6, 8, 10, 13, 15, 18, 20, 23]
        self.blackKeys = self.drawKeys(scene, self.blackKeyIndices, self.drawBlackKey)

        self.setScene(scene)
        self.updateUI()

    def getChordMappingString(self):
        chordMappingString = "Key Mappings:" + '\n'

        customMapping = self.keyboard.customMapping
        if customMapping:
            for key in customMapping:
                chordMappingString += QKeySequence(key).toString() + ': '

                for chord in customMapping[key]:
                    chordMappingString += "{}, ".format(chord.name)

                chordMappingString += '\n\n'

        else:
            chordMappingString += "None"
        return chordMappingString

    def updateKeys(self, keys, keyIndices, defaultColor):
        # inverts dict
        keyMappings = {val: key for key, val in self.keyboard.noteDict.iteritems()}

        for i in range(len(keys)):
            key = keys[i]
            curNote = key.note
            if curNote in self.keyboard.mapping_notes:
                key.setBrush(QColor(constants.highlighted_key_color))
            else:
                if self.pressedKeys[keyIndices[i]]:
                    key.setBrush(Qt.gray)
                else:
                    key.setBrush(defaultColor)

            # Update key mapping string
            note = constants.DiscreteNotes(keyIndices[i])
            key.mappingLabel.setPlainText(QKeySequence(keyMappings[note]).toString())
            for k, v in self.keyboard.customMapping.iteritems():
                if str(note) in str(v):
                    key.mappingLabel.setPlainText(QKeySequence(k).toString())
                    break
                elif keyMappings[note] == k:
                    key.mappingLabel.setPlainText("")

    def updateUI(self):
        # Make sure the pressedKeys exists
        if not hasattr(self, 'pressedKeys') or self.pressedKeys is None:
            self.pressedKeys = [False] * 24

        self.chordMappings.setPlainText(self.getChordMappingString())

        #update octaves seen on screen
        self.octaveLeft.setPlainText("Octave: " + str(self.keyboard.octave))
        self.octaveRight.setPlainText("Octave: " + str(self.keyboard.octave + 1))

        self.updateKeys(self.whiteKeys, self.whiteKeyIndices, Qt.white)
        self.updateKeys(self.blackKeys, self.blackKeyIndices, Qt.black)

        self.scene().update(self.scene().sceneRect())

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        #if the key pressed is a command, return
        #command mapper takes care of the command's actions
        if self.keyboard.commandMapper(event.key()):
            # TODO: only used for updateOctave(), refactor
            self.updateUI()
            return

        #note mapper maps a key to a note
        #returns false if key is not maped to a note
        notes = self.keyboard.noteMapper(event.key())

        #if key is mapped to a note, start the note
        for note in notes:
            print 'Printing notes:' + str(note)
            self.keyboard.startNote(note)

            # Mark the key as pressed for the UI
            self.pressedKeys[note.value] = True
            self.updateUI()

        if not notes:
            #else the key pressed does nothing currently
            print("key not mapped")

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        #key release only matters for notes
        #because notes can be held
        notes = self.keyboard.noteMapper(event.key())

        #if the key is mapped, end the note
        for note in notes:
            self.keyboard.endNote(note)

            # Mark the key as released for the UI
            self.pressedKeys[note.value] = False
            self.updateUI()

    def keyboardTypeButtonEvent(self):
        dialog_output = QInputDialog().getItem(self, 'Select Keyboard Type',
                '', constants.keyboard_types.keys())
        if self.keyboard.defaultButton(dialog_output):
            self.updateUI()

    def saveButtonEvent(self):
        if not self.keyboard.customMapping:
            return False

        # Save popup
        dialog_output = QInputDialog().getText(self, 'Save Key Mapping', 'Enter key mapping name here')
        self.keyboard.saveButton(dialog_output)

    def resetButtonEvent(self):
        if self.keyboard.resetButton():
            self.updateUI()

    def loadButtonEvent(self):
        mapping_names = self.keyboard.getMappingNames()
        dropdown_options = [' - '] + [i[0] for i in mapping_names]
        dialog_output = QInputDialog().getItem(self, 'Load Key Mapping',
                'Select key mapping', dropdown_options)

        if self.keyboard.loadButton(dialog_output):
            self.updateUI()

    def deleteButtonEvent(self):
        mapping_names = self.keyboard.getMappingNames()
        dropdown_options = [' - '] + [i[0] for i in mapping_names]
        dialog_output = QInputDialog().getItem(self, 'Delete Saved Key Mapping',
                'Delete key mapping (PERMANENT)', dropdown_options)

        self.keyboard.deleteButton(dialog_output)
