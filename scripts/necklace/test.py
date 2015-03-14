import pymel.core as pm
import necklace.lib as nlib


def create():
    curve = pm.circle()[0]

    necklaceNode = nlib.attachNecklace(curve)

    numSample = 15

    necklaceNode.numSample.set(numSample)
    necklaceNode.upVector2.set(1)

    for idx in range(numSample):
        geo = pm.duplicate('axisgeo')[0]

        pm.connectAttr(necklaceNode.outPosition[idx].outPosition,geo.translate)
        pm.connectAttr(necklaceNode.outRotation[idx].outRotation,geo.rotate)
  