import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

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

    self.lesionList = None
    self.lesionListTags = []

    # Instantiate and connect widgets ...

    self.sectorMapWidget = self.loadSectorMapUi()

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
    scansFormLayout = qt.QFormLayout(scansCollapsibleButton)

    #
    # T2 volume selector
    #
    self.t2VolumeSelector = slicer.qMRMLNodeComboBox()
    self.t2VolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.t2VolumeSelector.selectNodeUponCreation = True
    self.t2VolumeSelector.addEnabled = True
    self.t2VolumeSelector.removeEnabled = True
    self.t2VolumeSelector.noneEnabled = True
    self.t2VolumeSelector.showHidden = False
    self.t2VolumeSelector.showChildNodeTypes = False
    self.t2VolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.t2VolumeSelector.setToolTip( "Pick the T2 Prostate scan.")
    scansFormLayout.addRow("T2: ", self.t2VolumeSelector)

    #
    # T1 volume selector
    #
    self.t1VolumeSelector = slicer.qMRMLNodeComboBox()
    self.t1VolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.t1VolumeSelector.selectNodeUponCreation = True
    self.t1VolumeSelector.addEnabled = True
    self.t1VolumeSelector.removeEnabled = True
    self.t1VolumeSelector.noneEnabled = True
    self.t1VolumeSelector.showHidden = False
    self.t1VolumeSelector.showChildNodeTypes = False
    self.t1VolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.t1VolumeSelector.setToolTip( "Pick the T1 Prostate scan.")
    scansFormLayout.addRow("T1: ", self.t1VolumeSelector)

    #
    # mpMRI volume selector
    #
    self.mpMRIVolumeSelector = slicer.qMRMLNodeComboBox()
    self.mpMRIVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.mpMRIVolumeSelector.selectNodeUponCreation = True
    self.mpMRIVolumeSelector.addEnabled = True
    self.mpMRIVolumeSelector.removeEnabled = True
    self.mpMRIVolumeSelector.noneEnabled = True
    self.mpMRIVolumeSelector.showHidden = False
    self.mpMRIVolumeSelector.showChildNodeTypes = False
    self.mpMRIVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.mpMRIVolumeSelector.setToolTip( "Pick the mpMRI Prostate scan.")
    scansFormLayout.addRow("mpMRI: ", self.mpMRIVolumeSelector)

    #
    # DWI volume selector
    #
    self.dwiVolumeSelector = slicer.qMRMLNodeComboBox()
    self.dwiVolumeSelector.nodeTypes = ["vtkMRMLDiffusionWeightedVolumeNode"]
    self.dwiVolumeSelector.selectNodeUponCreation = True
    self.dwiVolumeSelector.addEnabled = True
    self.dwiVolumeSelector.removeEnabled = True
    self.dwiVolumeSelector.noneEnabled = True
    self.dwiVolumeSelector.showHidden = False
    self.dwiVolumeSelector.showChildNodeTypes = False
    self.dwiVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.dwiVolumeSelector.setToolTip( "Pick the DWI Prostate scan.")
    scansFormLayout.addRow("DWI: ", self.dwiVolumeSelector)

    #
    # ADC volume selector
    #
    self.adcVolumeSelector = slicer.qMRMLNodeComboBox()
    self.adcVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.adcVolumeSelector.selectNodeUponCreation = True
    self.adcVolumeSelector.addEnabled = True
    self.adcVolumeSelector.removeEnabled = True
    self.adcVolumeSelector.noneEnabled = True
    self.adcVolumeSelector.showHidden = False
    self.adcVolumeSelector.showChildNodeTypes = False
    self.adcVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.adcVolumeSelector.setToolTip( "Pick the ADC Prostate scan.")
    scansFormLayout.addRow("ADC: ", self.adcVolumeSelector)

    #
    # DCE volume selector
    #
    self.dceVolumeSelector = slicer.qMRMLNodeComboBox()
    self.dceVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.dceVolumeSelector.selectNodeUponCreation = True
    self.dceVolumeSelector.addEnabled = True
    self.dceVolumeSelector.removeEnabled = True
    self.dceVolumeSelector.noneEnabled = True
    self.dceVolumeSelector.showHidden = False
    self.dceVolumeSelector.showChildNodeTypes = False
    self.dceVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.dceVolumeSelector.setToolTip( "Pick the DCE Prostate scan.")
    scansFormLayout.addRow("DCE: ", self.dceVolumeSelector)


    #
    # Lesions Area
    #
    lesionsCollapsibleButton = ctk.ctkCollapsibleButton()
    lesionsCollapsibleButton.text = "Lesions"
    self.layout.addWidget(lesionsCollapsibleButton)

    # Layout within the dummy collapsible button
    lesionsFormLayout = qt.QFormLayout(lesionsCollapsibleButton)

    #
    # Lesion target list selector
    #
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
    lesionsFormLayout.addRow("Lesion Target List: ", self.targetListSelector)

    # Sector map
    lesionsFormLayout.addRow("Prostate sector: ", self.sectorMapWidget)
    
    # Add a lesion, pops up a sector widget to set where it is
    self.addLesionButton = qt.QPushButton()
    self.addLesionButton.text = 'Add Lesion'
    lesionsFormLayout.addRow("", self.addLesionButton)

    #
    # Set up Connections
    #
    # Volumes
    self.t2VolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectT2)
    self.t1VolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectT1)
    self.mpMRIVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectmpMRI)
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

    # Add vertical spacer
    self.layout.addStretch(1)


  def loadSectorMapUi(self):
    uiPathBase = os.path.join(os.path.dirname(__file__), 'Resources', 'UI')
    uiPath = os.path.join(uiPathBase, 'SectorMap.ui')
    uiFile = qt.QFile(uiPath)
    uiFile.open(qt.QFile.ReadOnly)
    sectorMapWidget = qt.QWidget()
    sectorMapWidget = self.uiLoader.load(uiFile)
    return sectorMapWidget
  
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

  def onSelectT2(self):
    vol = self.t2VolumeSelector.currentNode()
  def onSelectT1(self):
    vol = self.t1.VolumeSelector.currentNode()
  def onSelectmpMRI(self):
    vol = self.mpMRIVolumeSelector.currentNode()
  def onSelectDWI(self):
    vol = self.dwiVolumeSelector.currentNode()
  def onSelectADC(self):
    vol = self.adcVolumeSelector.currentNode()
  def onSelectDCE(self):
    vol = self.dceVolumeSelector.currentNode()
    

  def onApplyButton(self):
    self.logic.run(self.targetListSelector.currentNode(), self.t2VolumeSelector.currentNode(), self.t1VolumeSelector.currentNode(), self.mpMRIVolumeSelector.currentNode(), self.dwiVolumeSelector.currentNode(), self.adcVolumeSelector.currentNode(), self.dceVolumeSelector.currentNode())

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

  def run(self, t2Volume, t1Volume, mpMRIVolume, dwiVolume, adcVolume, dceVolume, targetList):
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
