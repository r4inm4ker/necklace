#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################
# necklaceNode.py
# Original Author: Jefri Haryono
#

###############################################################################
# Module docstring
###############################################################################
u"""a plugin node that generate points and orientations on curve."""

import sys

import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om

# Plug-in information:
kPluginNodeName = 'necklace'
kPluginNodeClassify = 'utility/general'
kPluginNodeId = om.MTypeId(0x87009)


class Necklace(omMPx.MPxNode):
    # node attributes
    inputCurve = om.MObject()
    upVector = om.MObject()
    frontAxis = om.MObject()
    upAxis = om.MObject()
    twist = om.MObject()
    uShift = om.MObject()
    numSample = om.MObject()
    outPosition = om.MObject()
    outRotations = om.MObject()
    isLoop = om.MObject()

    def __init__(self):
        omMPx.MPxNode.__init__(self)
        self.lastNumSample = -1

    @staticmethod
    def getParamFromLength(curveFn, currLength, maxLength, isLoopEnabled):
        if currLength < 0:
            if isLoopEnabled:
                currLength = maxLength - (-currLength % maxLength)
            else:
                currLength = 0

        elif currLength > maxLength:
            if isLoopEnabled:
                currLength = currLength % maxLength
            else:
                currLength = maxLength

        return curveFn.findParamFromLength(currLength)

    @staticmethod
    def _getIncrement(nSample, maxLength):
        if nSample < 2:
            addLen = maxLength
        else:
            addLen = maxLength / (nSample - 1)

        return addLen

    def compute(self, pPlug, data):
        """ compute functions.
        """
        # get inputs
        handle = data.inputValue(Necklace.inputCurve)
        inCurve = handle.asNurbsCurveTransformed()
        curveFn = om.MFnNurbsCurve(inCurve)
        maxLength = curveFn.length()

        handle = data.inputValue(Necklace.frontAxis)
        frontAxis = handle.asUChar()

        handle = data.inputValue(Necklace.upAxis)
        upAxis = handle.asUChar()

        handle = data.inputValue(Necklace.upVector)
        upVector = handle.asDouble3()

        handle = data.inputValue(Necklace.twist)
        twist = handle.asDouble()

        handle = data.inputValue(Necklace.numSample)
        nSample = handle.asInt()

        handle = data.inputValue(Necklace.isLoop)
        isLoopEnabled = handle.asBool()

        # prepare outputs
        pOutArray = data.outputArrayValue(Necklace.outPosition)
        rOutArray = data.outputArrayValue(Necklace.outRotation)

        # we might need to generate uShift if it's not inititated yet.
        uShiftArray = data.outputArrayValue(Necklace.uShift)

        if self.lastNumSample != nSample:
            self.lastNumSample = nSample
            posBuilder = om.MArrayDataBuilder(data, Necklace.outPosition, nSample)
            rotBuilder = om.MArrayDataBuilder(data, Necklace.outRotation, nSample)
            uShiftBuilder = om.MArrayDataBuilder(data, Necklace.uShift, nSample)
            for idx in range(nSample):
                handle = uShiftBuilder.addElement(idx)
                handle.setDouble(0.0)
            uShiftArray.set(uShiftBuilder)

        else:
            posBuilder = om.MArrayDataBuilder(pOutArray.builder())
            rotBuilder = om.MArrayDataBuilder(rOutArray.builder())

        xvec = om.MVector(1, 0, 0)
        yvec = om.MVector(0, 1, 0)
        zvec = om.MVector(0, 0, 1)

        pt = om.MPoint()
        currLen = 0
        increment = self._getIncrement(nSample, maxLength)
        for idx in range(nSample):
            uShiftArray.jumpToElement(idx)
            handle = uShiftArray.inputValue()
            currShift = handle.asDouble()

            param = self.getParamFromLength(curveFn, currLen + currShift, maxLength, isLoopEnabled)
            curveFn.getPointAtParam(param, pt)
            currLen += increment

            # create transformation matrix from this point in param
            tangent = curveFn.tangent(param, om.MSpace.kObject)
            up = om.MVector(*upVector)
            if abs(twist) > 1e-5:
                up = up.rotateBy(om.MQuaternion(twist, tangent))

            tangent = tangent.normal()
            cross1 = (tangent ^ up)
            normal = (cross1 ^ tangent).normal()
            bitangent = (tangent ^ normal).normal()

            mat = [tangent.x, tangent.y, tangent.z, 0,
                   normal.x, normal.y, normal.z, 0,
                   bitangent.x, bitangent.y, bitangent.z, 0,
                   pt.x, pt.y, pt.z, 1,
            ]
            mmat = om.MMatrix()
            om.MScriptUtil.createMatrixFromList(mat, mmat)
            transMat = om.MTransformationMatrix(mmat)

            # need to simplify this later (maybe using a generalized transformation matrix to rotate)
            if frontAxis == 0 and upAxis == 1:
                finalMat = transMat
            elif frontAxis == 0 and upAxis == 2:
                quat = om.MQuaternion(-0.5 * 3.141593, xvec)
                finalMat = transMat.rotateBy(quat, om.MSpace.kObject)
            elif frontAxis == 1 and upAxis == 2:
                quat = om.MQuaternion(-0.5 * 3.141593, zvec)
                quat2 = om.MQuaternion(-0.5 * 3.141593, yvec)
                quat = quat2 * quat
                finalMat = transMat.rotateBy(quat, om.MSpace.kObject)
            elif frontAxis == 1 and upAxis == 0:
                quat = om.MQuaternion(-0.5 * 3.141593, zvec)
                quat2 = om.MQuaternion(-1.0 * 3.141593, yvec)
                quat = quat2 * quat
                finalMat = transMat.rotateBy(quat, om.MSpace.kObject)
            elif frontAxis == 2 and upAxis == 0:
                quat = om.MQuaternion(0.5 * 3.141593, yvec)
                quat2 = om.MQuaternion(0.5 * 3.141593, zvec)
                quat = quat2 * quat
                finalMat = transMat.rotateBy(quat, om.MSpace.kObject)
            elif frontAxis == 2 and upAxis == 1:
                quat = om.MQuaternion(0.5 * 3.141593, yvec)
                finalMat = transMat.rotateBy(quat, om.MSpace.kObject)
            else:
                finalMat = transMat

            pos = finalMat.getTranslation(om.MSpace.kWorld)

            eulerRot = finalMat.eulerRotation()

            rotx = om.MAngle(eulerRot.x).asDegrees()
            roty = om.MAngle(eulerRot.y).asDegrees()
            rotz = om.MAngle(eulerRot.z).asDegrees()

            outHandle = posBuilder.addElement(idx)
            outHandle.set3Double(pos.x, pos.y, pos.z)

            outHandle = rotBuilder.addElement(idx)
            outHandle.set3Double(rotx, roty, rotz)

        pOutArray.set(posBuilder)
        rOutArray.set(rotBuilder)

        pOutArray.setAllClean()
        rOutArray.setAllClean()


# Plug-in initialization.
def nodeCreator():
    """ Creates an instance of our node class and delivers it to Maya as a pointer. """
    return omMPx.asMPxPtr(Necklace())


def nodeInitializer():
    nAttr = om.MFnNumericAttribute()
    tAttr = om.MFnTypedAttribute()
    eAttr = om.MFnEnumAttribute()
    inputAffects = []
    outputAffects = []

    Necklace.inputCurve = tAttr.create("inputCurve", "in", om.MFnData.kNurbsCurve)
    tAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.inputCurve)
    inputAffects.append(Necklace.inputCurve)

    Necklace.frontAxis = eAttr.create("frontAxis", "fa", 0)
    eAttr.addField('x', 0)
    eAttr.addField('y', 1)
    eAttr.addField('z', 2)
    eAttr.setStorable(True)
    eAttr.setKeyable(True)
    eAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.frontAxis)
    inputAffects.append(Necklace.frontAxis)

    Necklace.upAxis = eAttr.create("upAxis", "ua", 1)
    eAttr.addField('x', 0)
    eAttr.addField('y', 1)
    eAttr.addField('z', 2)
    eAttr.setStorable(True)
    eAttr.setKeyable(True)
    eAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.upAxis)
    inputAffects.append(Necklace.upAxis)

    Necklace.upVector = nAttr.create("upVector", "up", om.MFnNumericData.k3Double)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.upVector)
    inputAffects.append(Necklace.upVector)

    Necklace.twist = nAttr.create("twist", "twi", om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.twist)
    inputAffects.append(Necklace.twist)

    Necklace.isLoop = nAttr.create("loop", "lp", om.MFnNumericData.kBoolean)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.isLoop)
    inputAffects.append(Necklace.isLoop)

    Necklace.numSample = nAttr.create("numSample", "ns", om.MFnNumericData.kLong, 1)
    nAttr.setMin(0)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    Necklace.addAttribute(Necklace.numSample)
    inputAffects.append(Necklace.numSample)

    Necklace.uShift = nAttr.create("uVal", "u", om.MFnNumericData.kDouble, 0.0)
    nAttr.setArray(True)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setReadable(True)
    nAttr.setConnectable(True)
    nAttr.setUsesArrayDataBuilder(True)
    Necklace.addAttribute(Necklace.uShift)
    inputAffects.append(Necklace.uShift)

    Necklace.outPosition = nAttr.create("outPosition", "oup", om.MFnNumericData.k3Double)
    nAttr.setArray(True)
    nAttr.setStorable(False)
    nAttr.setHidden(False)
    nAttr.setReadable(True)
    nAttr.setWritable(False)
    nAttr.setUsesArrayDataBuilder(True)
    Necklace.addAttribute(Necklace.outPosition)
    outputAffects.append(Necklace.outPosition)

    Necklace.outRotation = nAttr.create("outRotation", "our", om.MFnNumericData.k3Double)
    nAttr.setArray(True)
    nAttr.setStorable(False)
    nAttr.setHidden(False)
    nAttr.setReadable(True)
    nAttr.setWritable(False)
    nAttr.setUsesArrayDataBuilder(True)
    Necklace.addAttribute(Necklace.outRotation)
    outputAffects.append(Necklace.outRotation)

    for outAttr in outputAffects:
        for inAttr in inputAffects:
            Necklace.attributeAffects(inAttr, outAttr)


def initializePlugin(mobject):
    """ Initialize the plug-in """
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write("Failed to register node: " + kPluginNodeName)
        raise


def uninitializePlugin(mobject):
    """ Uninitializes the plug-in """
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write('Failed to deregister node: ' + kPluginNodeName)
        raise     

