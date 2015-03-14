import pymel.core as pm

def attachNecklace(curveNode):
    curveNode = pm.PyNode(curveNode)
    curveNode.scale.set(4,4,4)

    necklaceNode = pm.createNode('necklace')

    curveNode.worldSpace[0] >> necklaceNode.inputCurve

    return necklaceNode