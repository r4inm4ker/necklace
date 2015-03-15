import pymel.core as pm

def loadPlugin():
    if not pm.pluginInfo("necklaceNode",q=1,loaded=True):
        pm.loadPlugin("necklaceNode.py")

def attachNecklace(curveNode):
    curveNode = pm.PyNode(curveNode)
    curveNode.scale.set(4,4,4)

    loadPlugin()
    necklaceNode = pm.createNode('necklace')

    curveNode.worldSpace[0] >> necklaceNode.inputCurve

    return necklaceNode