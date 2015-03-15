import pymel.core as pm
import necklace.lib as nlib

def create():
    pm.mel.eval('file -f -new;')
    pm.importFile('E:/git/brainyart/necklace/scenes/axisgeo.ma', namespace='axisgeo1')

    curve = pm.circle()[0]

    necklaceNode = nlib.attachNecklace(curve)

    numSample = 15

    necklaceNode.numSample.set(numSample)
    necklaceNode.upVector.set(0,0,1)

    for idx in range(numSample):
        geo = pm.duplicate('axisgeo1:axisgeo')[0]
        pm.connectAttr(necklaceNode.outPosition[idx].outPosition,geo.translate)
        pm.connectAttr(necklaceNode.outRotation[idx].outRotation,geo.rotate)
  