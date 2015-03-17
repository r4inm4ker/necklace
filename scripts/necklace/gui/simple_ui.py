#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jefri Haryono
# @Email : jefri.yeh@gmail.com

import pymel.core as pm
import necklace.lib as nlib


class NecklaceSimpleUI():
    uiName = 'necklaceSimpleUI'
    uiTitle = 'Necklace Simple UI'
    necklaceName = 'testNecklaceNode'
    tmpGrp = 'necklaceDupGrp'

    def ui(self):
        if pm.window(self.uiName, q=True, ex=True):
            pm.deleteUI(self.uiName)

        win = pm.window(self.uiName, title=self.uiTitle)
        with win:
            mainForm = pm.formLayout()
            with mainForm:
                hori = pm.horizontalLayout()
                with hori:
                    pm.text(w=80, label='curve: ')
                    self.curveTF = pm.textField(w=80)
                    pm.button('<<<', w=40, command=pm.Callback(self.updateCurveTF))
                hori.redistribute(0, 0, 0)

                hori = pm.horizontalLayout()
                with hori:
                    pm.text(w=80, label='geo: ')
                    self.geoTF = pm.textField(w=80)
                    pm.button('<<<', w=40, command=pm.Callback(self.updateGeoTF))
                hori.redistribute(0, 0, 0)

                hori = pm.horizontalLayout()
                with hori:
                    pm.text(w=80, label='num sample: ')
                    self.numSampleIF = pm.intField(w=80, value=1)
                hori.redistribute(0, 0)

                pm.separator(h=10)

                pm.button('create', command=pm.Callback(self.create))

            mainForm.redistribute(*[0] * mainForm.getNumberOfChildren())
        win.show()

    @classmethod
    def launch(cls):
        inst = cls().ui()


    def updateCurveTF(self):
        sel = pm.ls(sl=1)
        if sel:
            curve = sel[0]
            self.curveTF.setText(curve)

    def updateGeoTF(self):
        sel = pm.ls(sl=1)
        if sel:
            geo = sel[0]
            self.geoTF.setText(geo)

    def create(self):
        curve = self.curveTF.getText()
        geo = self.geoTF.getText()


        if curve and geo:
            curveNode = pm.PyNode(curve)
            geoNode = pm.PyNode(geo)

            if pm.objExists(self.necklaceName):
                pm.delete(self.necklaceName)

            if pm.objExists(self.tmpGrp):
                pm.delete(self.tmpGrp)

            necklaceNode = nlib.attachNecklace(curveNode)
            pm.rename(necklaceNode, self.necklaceName)
            numSample = self.numSampleIF.getValue()
            necklaceNode.numSample.set(numSample)

            tmpGrp = pm.createNode('transform', name=self.tmpGrp)

            for idx in range(numSample):
                geo = pm.duplicate(geoNode)[0]
                pm.connectAttr(necklaceNode.outPosition[idx].outPosition, geo.translate)
                pm.connectAttr(necklaceNode.outRotation[idx].outRotation, geo.rotate)

                pm.parent(geo, tmpGrp)

def launch():
    NecklaceSimpleUI.launch()
