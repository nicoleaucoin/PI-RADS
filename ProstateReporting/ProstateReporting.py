import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from datetime import datetime

#
# ProstateReporting
#

class ProstateReporting(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Prostate Reporting"
    self.parent.categories = ["ProstateBx.PI-RADS"]
    self.parent.dependencies = []
    self.parent.contributors = ["Nicole Aucoin (Harmonus Inc.)"]
    self.parent.helpText = """
    This is a scripted loadable module to support Prostate Imaging Reporting.
    It allows a user to categorise lesions.
    """
    self.parent.acknowledgementText = """
    Information given in this module is based on PI-RADS(tm) Prostate
    Imaging - Reporting and Data System 2015, version 2, from the American
    College of Radiology.
    """ # replace with organization, grant and thanks.

#
# ProstateReportingWidget
#

class ProstateReportingWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = ProstateReportingLogic()

    self.uiLoader = qt.QUiLoader()

    self.patientName = None

    self.lesionList = None
    self.lesionListTags = []

    # Instantiate and connect widgets ...

    # Load UI files
    self.scansWidget = self.loadUI('Scans')
    self.sectorMapWidget = self.loadUI('SectorMap')
    self.assessmentWidget = self.loadUI('Assessment')
    self.reportWidget = self.loadUI('Report')

    # Set up the sector relationships
    self.SectorMap = None
    self.initSectorMap()

    #
    # Volumes Area
    #
    scansCollapsibleButton = ctk.ctkCollapsibleButton()
    scansCollapsibleButton.text = "Patient Scans"
    self.layout.addWidget(scansCollapsibleButton)

    # Layout within the dummy collapsible button
    scansLayout = qt.QVBoxLayout(scansCollapsibleButton)

    # Patient name
    patientNameLayout = qt.QHBoxLayout()
    patientNameLayout.addWidget(qt.QLabel("Patient Name:"))
    self.patientNameLabel = qt.QLabel("")
    patientNameLayout.addWidget(self.patientNameLabel)

    scansLayout.addLayout(patientNameLayout)

    # Scans
    scansLayout.addWidget(self.scansWidget)

    self.t2VolumeSelector = self.logic.getChild(self.scansWidget, 't2VolumeSelector')
    self.t2VolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.t2ScanDateLabel = self.logic.getChild(self.scansWidget, 't2ScanDateLabel')

    self.t1VolumeSelector = self.logic.getChild(self.scansWidget, 't1VolumeSelector')
    self.t1VolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.t1ScanDateLabel = self.logic.getChild(self.scansWidget, 't1ScanDateLabel')

    self.dwiVolumeSelector = self.logic.getChild(self.scansWidget, 'dwiVolumeSelector')
    self.dwiVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.dwiScanDateLabel = self.logic.getChild(self.scansWidget, 'dwiScanDateLabel')

    self.adcVolumeSelector = self.logic.getChild(self.scansWidget, 'adcVolumeSelector')
    self.adcVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.adcScanDateLabel = self.logic.getChild(self.scansWidget, 'adcScanDateLabel')

    self.dceVolumeSelector = self.logic.getChild(self.scansWidget, 'dceVolumeSelector')
    self.dceVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.dceScanDateLabel = self.logic.getChild(self.scansWidget, 'dceScanDateLabel')

    #
    # Lesions Area
    #
    lesionsCollapsibleButton = ctk.ctkCollapsibleButton()
    lesionsCollapsibleButton.text = "Lesions"
    self.layout.addWidget(lesionsCollapsibleButton)

    # Layout within the dummy collapsible button
    lesionsLayout = qt.QVBoxLayout(lesionsCollapsibleButton)

    # Sector map
    sectorMapLabel = qt.QLabel()
    sectorMapLabel.setText("Prostate sector:")
    lesionsLayout.addWidget(sectorMapLabel)
    lesionsLayout.addWidget(self.sectorMapWidget)

    # Lesion target list
    if 0:
      self.targetListSelector = slicer.qMRMLNodeComboBox()
      self.targetListSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
      self.targetListSelector.selectNodeUponCreation = True
      self.targetListSelector.addEnabled = True
      self.targetListSelector.removeEnabled = False
      self.targetListSelector.noneEnabled = False
      self.targetListSelector.showHidden = False
      self.targetListSelector.showChildNodeTypes = False
      self.targetListSelector.setMRMLScene( slicer.mrmlScene )
      self.targetListSelector.setToolTip( "Pick the list of target lesion fiducials.")
      lesionsLayout.addWidget(self.targetListSelector)

    # Add a lesion, will create a list if necessary. Will name it according
    # to sector selection
    self.addLesionButton = qt.QPushButton()
    self.addLesionButton.text = 'Add Lesion'
    lesionsLayout.addWidget(self.addLesionButton)

    # show the lesions in a table
    self.targetTableWidget = slicer.qSlicerSimpleMarkupsWidget()
    self.targetTableWidget.setMRMLScene( slicer.mrmlScene )
    lesionsLayout.addWidget(self.targetTableWidget)
    self.targetListSelector = self.logic.getChild(self.targetTableWidget, "MarkupsFiducialNodeComboBox")
    # hide the place button as want to rename fids when adding
    placeWidget = self.logic.getChild(self.targetTableWidget, "PlaceButton")
    placeWidget.hide()


    #
    # Assessment Area
    #
    assessmentCollapsibleButton = ctk.ctkCollapsibleButton()
    assessmentCollapsibleButton.text = "Assessment"
    self.layout.addWidget(assessmentCollapsibleButton)

    # Layout within the dummy collapsible button
    assessmentLayout = qt.QVBoxLayout(assessmentCollapsibleButton)

    assessmentLayout.addWidget(self.assessmentWidget)
    self.assessmentComboBox = self.logic.getChild(self.assessmentWidget, "assessmentComboBox")

    #
    # Report Area
    #
    self.reportButton = qt.QPushButton()
    self.reportButton.setText("Report")
    self.layout.addWidget(self.reportButton)

    # get the report widgets need to fill in
    self.reportPatientName = self.logic.getChild(self.reportWidget, "patientNameLabel")
    self.reportScans = self.logic.getChild(self.reportWidget, "patientScansTextEdit")
    self.reportLesions = self.logic.getChild(self.reportWidget, "patientLesionsTextEdit")
    self.reportAssessment = self.logic.getChild(self.reportWidget, "patientAssessmentTextEdit")
    self.reportNotes = self.logic.getChild(self.reportWidget, "patientNotesTextEdit")
    self.reportSave = self.logic.getChild(self.reportWidget, "savePushButton")
    self.reportCancel = self.logic.getChild(self.reportWidget, "cancelPushButton")
    #
    # Set up Connections
    #
    # Volumes
    self.t2VolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectT2)
    self.t1VolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectT1)
    self.dwiVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectDWI)
    self.adcVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectADC)
    self.dceVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectDCE)
    
    # Lesions
    self.targetListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectTargets)

    # Sector map
    self.LRComboBox.connect("currentIndexChanged(int)", self.onSectorLRChanged)
    self.ZoneComboBox.connect("currentIndexChanged(int)", self.onSectorZoneChanged)
    self.GlandComboBox.connect("currentIndexChanged(int)", self.onSectorGlandChanged)
    self.APComboBox.connect("currentIndexChanged(int)", self.onSectorAPChanged)

    self.addLesionButton.connect('clicked(bool)',self.onAddLesion)

    # Report
    self.reportButton.connect('clicked(bool)', self.onReportButton)
    self.reportSave.connect('clicked(bool)', self.onReportSave)
    self.reportCancel.connect('clicked(bool)', self.onReportCancel)

    # Add vertical spacer
    self.layout.addStretch(1)


  def loadUI(self, uiName):
    uiPathBase = os.path.join(os.path.dirname(__file__), 'Resources', 'UI')
    uiPath = os.path.join(uiPathBase, uiName + '.ui')
    uiFile = qt.QFile(uiPath)
    uiFile.open(qt.QFile.ReadOnly)
    widget = qt.QWidget()
    widget = self.uiLoader.load(uiFile)
    return widget
  
  def cleanup(self):
    self.removeObservers()

  def removeObservers(self):
    # remove observers on local variables
    if self.lesionList is not None:
      print 'Removing observers on lesion list'
      for tag in self.lesionListTags:
        self.lesionList.RemoveObserver(tag)
    # clear the list of tags
    self.lesionListTags = []

  def addObservers(self):
    # add observers to the fiducials list to respond to fiducials added or changed
    self.removeObservers()
    
    if self.lesionList is None:
      print 'No fiducial list set to add obsevers to'
      return
    # add observations and save tags for later removal
    self.lesionListTags.append(self.lesionList.AddObserver(slicer.vtkMRMLMarkupsNode.MarkupAddedEvent, self.onLesionFiducialAdded))

  def initSectorMap(self):
    self.SectorMap = {}

    PZDict = {}
    PZDict['LR'] = ['Right (r)', 'Left (l)']
    PZDict['AP'] = ['Anterior (a)', 'Medial Posterior (mp)', 'Lateral Posterior (lp)']
    PZDict['Gland'] = ['Base (B)', 'Midgland (Mg)', 'Apex (A)']

    TZDict = {}
    TZDict['LR'] = ['Right (r)', 'Left (l)']
    TZDict['AP'] = ['Anterior (a)', 'Posterior (p)']
    TZDict['Gland'] = ['Base (B)', 'Midgland (Mg)', 'Apex (A)']

    CZDict = {}
    CZDict['LR'] = ['Right (r)', 'Left (l)']
    CZDict['AP'] = []
    CZDict['Gland'] = [] # ['Base (B)']


    ASDict = {}
    ASDict['LR'] = ['Right (r)', 'Left (l)']
    ASDict['AP'] = [] # ['Anterior (a)']
    ASDict['Gland'] = ['Base (B)', 'Midgland (Mg)', 'Apex (A)']

    
    SVDict = {}
    SVDict['LR'] = ['Right (r)', 'Left (l)']
    SVDict['AP'] = []
    SVDict['Gland'] = []

    USDict = {}
    USDict['LR'] = []
    USDict['AP'] = []
    USDict['Gland'] = [] # ['Apex (A)']


    self.SectorMap['Peripheral Zone (PZ)'] = PZDict
    self.SectorMap['Transition Zone (TZ)'] = TZDict
    self.SectorMap['Central Zone (CZ)'] = CZDict
    self.SectorMap['Anterior Fibromuscular Stroma (AS)'] = ASDict
    self.SectorMap['Seminal Vesicles (SV)'] = SVDict
    self.SectorMap['Urethral Sphincter (US)'] = USDict


    # Update the sector map drop down widgets
    self.ZoneComboBox = self.logic.getChild(self.sectorMapWidget, "zoneComboBox")
    self.LRComboBox = self.logic.getChild(self.sectorMapWidget, "LRComboBox")
    self.GlandComboBox = self.logic.getChild(self.sectorMapWidget, "glandComboBox")
    self.APComboBox = self.logic.getChild(self.sectorMapWidget, "APComboBox")

    self.ZoneComboBox.clear()
    # add the peripheral zone strings
    print 'SectorMap keys = ', self.SectorMap.keys()
    for zone in self.SectorMap:
      self.ZoneComboBox.addItem(zone)
    pz = 'Peripheral Zone (PZ)'
    self.fillComboBoxesFromZone(pz)

    # select the Peripheral zone defaults
    pzIndex = self.ZoneComboBox.findText(pz)
    print 'Selecting the PZ: index = ', pzIndex
    if pzIndex >= 0:
      self.ZoneComboBox.setCurrentIndex(pzIndex)
    gIndex = self.GlandComboBox.findText(self.SectorMap[pz]['Gland'][0])
    if gIndex >= 0:
      self.GlandComboBox.setCurrentIndex(gIndex)
    lrIndex =  self.LRComboBox.findText(self.SectorMap[pz]['LR'][0])
    if lrIndex >= 0:
      self.LRComboBox.setCurrentIndex(lrIndex)
    apIndex = self.APComboBox.findText(self.SectorMap[pz]['AP'][0])
    if apIndex >= 0:
      self.APComboBox.setCurrentIndex(apIndex)

  def enableDisableComboBox(self, comboBox):
    if comboBox.count == 0:
      comboBox.setEnabled(False)
    else:
      comboBox.setEnabled(True)

  def fillComboBoxesFromZone(self, zone):
    if not self.SectorMap.has_key(zone):
      print 'Invalid zone: ', zone
      return

    self.GlandComboBox.clear()
    for gland in self.SectorMap[zone]['Gland']:
      self.GlandComboBox.addItem(gland)
    self.enableDisableComboBox(self.GlandComboBox)

    self.LRComboBox.clear()
    for lr in self.SectorMap[zone]['LR']:
      self.LRComboBox.addItem(lr)
    self.enableDisableComboBox(self.LRComboBox)

    self.APComboBox.clear()
    for ap in self.SectorMap[zone]['AP']:
      self.APComboBox.addItem(ap)
    self.enableDisableComboBox(self.APComboBox)

  def onSelectTargets(self):
    # update for new fiducial list
    print 'onSelectTargets'
    fids = self.targetListSelector.currentNode()

  def onSectorZoneChanged(self, index):
    print 'onSectorZoneChanged: ', index
    txt = self.getSectorCode(self.ZoneComboBox)
    print '\t',txt
    self.fillComboBoxesFromZone(self.ZoneComboBox.currentText)
      
  def onSectorLRChanged(self, index):
    print 'onSectorLRChanged: ', index

  def onSectorGlandChanged(self, index):
    print 'onSectorGladChanged: ', index

  def onSectorAPChanged(self, index):
    print 'onSectorAPChanged: ', index
    
  def onAddLesion(self):
    # add a fiducial to the current lesions list
    self.lesionList = self.targetListSelector.currentNode()
    if self.lesionList is None:
      # creating a lesion list
      self.lesionList = slicer.vtkMRMLMarkupsFiducialNode()
      self.lesionList.SetName("Lesions")
      slicer.mrmlScene.AddNode(self.lesionList)
      self.targetListSelector.setCurrentNode(self.lesionList)
      self.addObservers()
      
    interactionNode = slicer.util.getNode("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()
    slicer.modules.markups.logic().SetActiveListID(self.lesionList)

  def onLesionFiducialAdded(self, caller, event):
    print 'onLesionFiducialAdded: caller = ', caller.GetID()
    if caller.IsA('vtkMRMLMarkupsFiducialNode'):
      # update the fid's name according to sector
      # assume that it's the same as self.lesionList
      lastFidIndex = self.lesionList.GetNumberOfFiducials() - 1
      sectorCode = self.getFullSectorCode()
      self.lesionList.SetNthFiducialLabel(lastFidIndex, sectorCode)

  def getSectorCode(self, comboBox):
    # Parse the current text of the combo box to get out the code in ()
    # Returns empty string on failure
    code = ''
    if comboBox is None:
      return code
    txt = comboBox.currentText
    if txt is not None and txt.find("(") is not -1:
      code = txt[txt.find("(")+1:txt.rfind(")")]
    return code

  def getFullSectorCode(self):
    # from the current sector map's settings, build up the code
    code = ''
    lrCode = self.getSectorCode(self.LRComboBox)
    zoneCode = self.getSectorCode(self.ZoneComboBox)
    apCode = self.getSectorCode(self.APComboBox)
    glandCode = self.getSectorCode(self.GlandComboBox)
    code =  zoneCode + apCode + glandCode + lrCode
    return code

  def getUIDForVolume(self, volumeNode):
    if volumeNode is None:
      return None
    snode = volumeNode.GetStorageNode()
    if snode is None:
      print 'getUIDForVolume: volume does not have a storage node'
      return None
    fileName = snode.GetFileName()
    if fileName is None:
      print 'getUIDForVolume: no file name on storage node'
      return None
    uid = slicer.dicomDatabase.instanceForFile(fileName)
    if uid is None:
      print 'getUIDForVolume: cannot find uid for file name ', fileName
      return None
    return uid

  # Get the patient name for this dicom volume.
  # Check to be sure that it matches the global patient name if that's set.
  # Return the patient name on success, None on failure.
  def checkPatientName(self, volumeNode):
    if volumeNode is None:
      print 'checkPatientName: no volume!'
      return None

    uid = self.getUIDForVolume(volumeNode)
    if uid is None:
      print 'checkPatientName: Unable to get DICOM uid for volume ', volumeNode.GetName()
      return None

    patientName = slicer.dicomDatabase.instanceValue(uid, "0010,0010")
    if patientName is None:
      print 'checkPatientName: cannot find patient name tag on instance', uid
      return None
    if (self.patientName is not None) and (self.patientName != patientName):
      print 'checkPatientName: ERROR: Patient name ', patientName, ' does not match already loaded scans patient name: ', self.patientName, '.\nUnsetting patient name, select new volumes.'
      return None
    print 'checkPatientName: valid name: ', patientName
    self.patientName = patientName
    return self.patientName

  def getScanDate(self, volumeNode):
    uid = self.getUIDForVolume(volumeNode)
    if uid is None:
      print 'checkPatientName: Unable to get DICOM uid for volume ', volumeNode.GetName()
      return None
    scanDate = slicer.dicomDatabase.instanceValue(uid, "0008,0022")
    if scanDate is None or scanDate == '':
      print 'getScanDate: unable to get the acquisition date for volume ', volumeNode.GetName()
      return None
    print 'getScanDate: got valid scan date: ', scanDate
    # Format it a bit more nicely. According to the DICOM standard this
    # attribute is in the format yyyymmdd
    datetime_object = datetime.strptime(scanDate, "%Y%m%d")
    scanDate = datetime_object.date()
    return scanDate

  def onSelectT2(self):
    vol = self.t2VolumeSelector.currentNode()
    self.patientNameLabel.setText(self.checkPatientName(vol))
    self.t2ScanDateLabel.setText(self.getScanDate(vol))

  def onSelectT1(self):
    vol = self.t1VolumeSelector.currentNode()
    self.patientNameLabel.setText(self.checkPatientName(vol))
    self.t1ScanDateLabel.setText(self.getScanDate(vol))

  def onSelectDWI(self):
    vol = self.dwiVolumeSelector.currentNode()
    self.patientNameLabel.setText(self.checkPatientName(vol))
    self.dwiScanDateLabel.setText(self.getScanDate(vol))

  def onSelectADC(self):
    vol = self.adcVolumeSelector.currentNode()
    self.patientNameLabel.setText(self.checkPatientName(vol))
    self.adcScanDateLabel.setText(self.getScanDate(vol))

  def onSelectDCE(self):
    vol = self.dceVolumeSelector.currentNode()
    self.patientNameLabel.setText(self.checkPatientName(vol))
    self.dceScanDateLabel.setText(self.getScanDate(vol))

  def onReportButton(self):
    # pop up the report widget and fill it in
    self.reportPatientName.setText('')
    self.reportScans.clear()
    self.reportLesions.clear()
    self.reportAssessment.clear()
    # TBD: clear notes?
    # self.reportNotes.clear()

    self.reportWidget.show()

    # Patient Name
    self.reportPatientName.setText(self.patientName)

    # Scans
    scansString = 'Selected Scans:\n'

    vol = self.t2VolumeSelector.currentNode()
    if vol is not None:
      scansString = scansString + '\nT2:\n' + vol.GetName() + '\nAcquired on ' + self.t2ScanDateLabel.text + '\n'

    vol = self.t1VolumeSelector.currentNode()
    if vol is not None:
      scansString = scansString + '\nT1:\n' + vol.GetName() + '\nAcquired on ' + self.t1ScanDateLabel.text + '\n'

    vol = self.dwiVolumeSelector.currentNode()
    if vol is not None:
      scansString = scansString + '\nDWI:\n' + vol.GetName() + '\nAcquired on ' + self.dwiScanDateLabel.text + '\n'

    vol = self.adcVolumeSelector.currentNode()
    if vol is not None:
      scansString = scansString + '\nADC:\n' + vol.GetName() + '\nAcquired on ' + self.adcScanDateLabel.text + '\n'

    vol = self.dceVolumeSelector.currentNode()
    if vol is not None:
      scansString = scansString + '\nDCE:\n' + vol.GetName() + '\nAcquired on ' + self.DCEScanDateLabel.text + '\n'

    self.reportScans.appendPlainText(scansString)

    # Lesions
    lesionsString = 'Selected Lesions:\n\n'
    lesionList = self.targetListSelector.currentNode()
    if lesionList is not None:
      numberOfLesions = lesionList.GetNumberOfFiducials()
      for i in range(numberOfLesions):
        pos = [0,0,0]
        lesionList.GetNthFiducialPosition(i, pos)
        posStr = '(%.3f, %.3f, %.3f)' % (pos[0], pos[1], pos[2])
        lesionsString = lesionsString + lesionList.GetNthFiducialLabel(i) + "  " + posStr + "\n"

    self.reportLesions.appendPlainText(lesionsString)

    # Assessment
    assessmentString = self.assessmentComboBox.currentText
    self.reportAssessment.appendPlainText(assessmentString)

  def onReportSave(self):
    # get the selected file name
    # use a scan directory parent as suggestion
    dirHint = ''
    vol = self.t2VolumeSelector.currentNode()
    if vol is not None:
      volumeFile = vol.GetStorageNode().GetFileName()
      dirHint = os.path.dirname(volumeFile)
    filterString = 'Report files (*.json *.csv *.html)'
    fileName = qt.QFileDialog.getSaveFileName(self, "Save Report", dirHint, filterString)
    print 'onReportSave: filename = ', fileName

    # save report

  def onReportCancel(self):
    self.reportWidget.close()

  def onApplyButton(self):
    self.logic.run(self.targetListSelector.currentNode(), self.t2VolumeSelector.currentNode(), self.t1VolumeSelector.currentNode(), self.dwiVolumeSelector.currentNode(), self.adcVolumeSelector.currentNode(), self.dceVolumeSelector.currentNode())

#
# ProstateReportingLogic
#

class ProstateReportingLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  #Get object of a widget by a given name
  def getChild(self, widget, objectName):
    if widget.objectName == objectName:
        return widget
    else:
        for w in widget.children():
            resulting_widget = self.getChild(w, objectName)
            if resulting_widget:
                return resulting_widget
        return None

  def run(self, t2Volume, t1Volume, dwiVolume, adcVolume, dceVolume, targetList):
    """
    Run the actual algorithm
    """


    logging.info('Processing started')



    logging.info('Processing completed')

    return True


class ProstateReportingTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ProstateReporting1()

  def test_ProstateReporting1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    self.delayDisplay('Test passed!')
