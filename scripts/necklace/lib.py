#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jefri Haryono
# @Email : jefri.yeh@gmail.com


import pymel.core as pm

def loadPlugin():
    if not pm.pluginInfo("necklaceNode",q=1,loaded=True):
        pm.loadPlugin("necklaceNode.py")

def attachNecklace(curveNode):
    curveNode = pm.PyNode(curveNode)

    loadPlugin()
    necklaceNode = pm.createNode('necklace')

    curveNode.worldSpace[0] >> necklaceNode.inputCurve

    return necklaceNode