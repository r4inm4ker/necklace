#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################
## CurvePointsNode.py
##
## desc: uniform points on curve node
## cate: CATEGORY
## depn: rig
## Original Author: Jefri Haryono
## subversion info:
## $Author$ last committing id
## $Date$
## $Revision$
##

###############################################################################
# Module docstring
###############################################################################
u'''uniform points on curve node.'''

import sys

import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om

# Plug-in information:
kPluginNodeName = 'curvePointsNode'
kPluginNodeClassify = 'utility/general'
kPluginNodeId = om.MTypeId(0x87009 )

##########################################################
# Plug-ins 
##########################################################

class CurvePointsNode(omMPx.MPxNode):
    inputCurve = om.MObject()
    upVector = om.MObject()
    twist = om.MObject()
    numSample = om.MObject()
    outPositions = om.MObject()
    shift = om.MObject()
    isLoop = om.MObject()
    frontAxis = om.MObject()
    upAxis = om.MObject()
    uVal = om.MObject()
    
    def __init__(self):
        ''' Constructor. '''
        omMPx.MPxNode.__init__(self)
        self.maxLength = 0
        self.lastNumSample = -1
        
    def getParamFromLength(self,currLength):
        
        if currLength < 0:
            if self.isLoopEnabled:
                currLength = self.maxLength - (-currLength % self.maxLength)
            else:
                currLength = 0
                
        elif currLength > self.maxLength:
            if self.isLoopEnabled:
                currLength = currLength % self.maxLength
            else:
                currLength = self.maxLength
        
        return self.curveFn.findParamFromLength(currLength)  
        
    def compute(self, pPlug, data):
        ''' compute functions.
        '''
          
        #===input plug data===#
        inputDataHandle = data.inputValue(CurvePointsNode.inputCurve)        
        
        inCurve = inputDataHandle.asNurbsCurveTransformed()
        
            
        curveFn = om.MFnNurbsCurve(inCurve)
        self.curveFn = curveFn
        
        frontAxisHandle = data.inputValue(CurvePointsNode.frontAxis)
        frontAxis = frontAxisHandle.asUChar()
        
        upAxisHandle = data.inputValue(CurvePointsNode.upAxis)
        upAxis = upAxisHandle.asUChar()
        
        upVectorHandle = data.inputValue(CurvePointsNode.upVector)
        upVector = upVectorHandle.asDouble3()
        
        twistHandle = data.inputValue(CurvePointsNode.twist)
        twist = twistHandle.asDouble()
        
        numSampleHandle = data.inputValue(CurvePointsNode.numSample)
        nSample = numSampleHandle.asInt()
        
        
        shiftHandle = data.inputValue(CurvePointsNode.shift)
        lengthShift = shiftHandle.asDouble()
        
        isLoopHandle = data.inputValue(CurvePointsNode.isLoop)
        self.isLoopEnabled = isLoopHandle.asBool()
        
        maxLength = curveFn.length()
        
        self.maxLength = maxLength
        
        currLen = 0 + lengthShift
        
        if nSample < 2:
            addLen = maxLength
        else:
            addLen = maxLength / (nSample-1)
        
        
        pOutArray = data.outputArrayValue(CurvePointsNode.outPositions)
        rOutArray = data.outputArrayValue(CurvePointsNode.outRotations)
        uValArray = data.outputArrayValue(CurvePointsNode.uVal)
        sameSample = True
        uValBuilder = None
        if self.lastNumSample != nSample:
            self.lastNumSample = nSample
            posBuilder = om.MArrayDataBuilder(data,CurvePointsNode.outPositions,nSample)
            rotBuilder = om.MArrayDataBuilder(data,CurvePointsNode.outRotations,nSample)
            
            
            uValBuilder = om.MArrayDataBuilder(data,CurvePointsNode.uVal,nSample)
            
            sameSample = False
          
        else:
            posBuilder = om.MArrayDataBuilder(pOutArray.builder())
            rotBuilder = om.MArrayDataBuilder(rOutArray.builder())
  
                      
            
        
        xv = om.MVector(1,0,0)
        yv = om.MVector(0,1,0)
        zv = om.MVector(0,0,1)
        
        up = om.MVector(upVector[0],upVector[1],upVector[2])
        pt = om.MPoint()
        for idx in range(nSample):
            
            if sameSample:
                if idx < uValArray.elementCount():
                    uValArray.jumpToElement(idx)
                    ihand = uValArray.inputValue()
                    currLen = ihand.asDouble()
            else:
                outHandle = uValBuilder.addElement(idx)
                outHandle.setDouble(currLen)
            
            
            param = self.getParamFromLength(currLen)
                
            curveFn.getPointAtParam(param,pt)
            
            tangent = curveFn.tangent(param,om.MSpace.kObject)
            if twist !=0.0:
                quat = om.MQuaternion(twist,tangent)
                finUp = up.rotateBy(quat)
            else:
                finUp = up
            
            tangent = tangent.normal()
            
            cross1  = (tangent^finUp)
            
            normal = (cross1^tangent).normal()
            
            bitangent = (tangent^normal).normal()
            
            
            mat = [tangent.x,   tangent.y,  tangent.z,  0,
                   normal.x,    normal.y,   normal.z,   0,
                   bitangent.x, bitangent.y,bitangent.z,0,
                   pt.x,        pt.y,       pt.z,       1,
                   ]
            
            mmat = om.MMatrix()
            
            om.MScriptUtil.createMatrixFromList(mat,mmat)
            
            transMat = om.MTransformationMatrix(mmat)
        
            
            if frontAxis ==0  and upAxis == 1:
                finalMat = transMat
            elif frontAxis == 0 and upAxis == 2:
                quat = om.MQuaternion(-0.5 * 3.141593,xv)
                finalMat = transMat.rotateBy(quat,om.MSpace.kObject)
   
            elif frontAxis == 1  and upAxis == 2:
                quat = om.MQuaternion(-0.5 * 3.141593,zv)
                quat2 = om.MQuaternion(-0.5 * 3.141593,yv)
                quat =  quat2*quat
                finalMat = transMat.rotateBy(quat,om.MSpace.kObject)
            
            elif frontAxis == 1  and upAxis == 0:
                quat = om.MQuaternion(-0.5 * 3.141593,zv)
                quat2 = om.MQuaternion(-1.0 * 3.141593,yv)
                quat =  quat2*quat
                finalMat = transMat.rotateBy(quat,om.MSpace.kObject)
            
            elif frontAxis == 2  and upAxis == 0:
                quat = om.MQuaternion(0.5 * 3.141593,yv)
                quat2 = om.MQuaternion(0.5 * 3.141593,zv)
                quat =  quat2*quat
                finalMat = transMat.rotateBy(quat,om.MSpace.kObject)
            
            elif frontAxis == 2  and upAxis == 1:
                quat = om.MQuaternion(0.5 * 3.141593,yv)
                finalMat = transMat.rotateBy(quat,om.MSpace.kObject)
                
            else:
                finalMat = transMat
            
            
        
            pos =  finalMat.getTranslation(om.MSpace.kWorld)
        
            eulerRot = finalMat.eulerRotation()
        
            rotx = om.MAngle(eulerRot.x).asDegrees()
            roty = om.MAngle(eulerRot.y).asDegrees()
            rotz = om.MAngle(eulerRot.z).asDegrees()
            
            
            
            outHandle = posBuilder.addElement(idx)
            outHandle.set3Double( pos.x,pos.y,pos.z)
            
            outHandle = rotBuilder.addElement(idx)
            outHandle.set3Double(rotx,roty,rotz)
            
            
            currLen = currLen + addLen
     
          
        if not sameSample and uValBuilder:
             uValArray.set(uValBuilder)

        
        pOutArray.set(posBuilder)
        rOutArray.set(rotBuilder)
        pOutArray.setClean()
        rOutArray.setClean()
        pOutArray.setAllClean()
        rOutArray.setAllClean()
        data.setClean(pPlug)
    
##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():
    ''' Creates an instance of our node class and delivers it to Maya as a pointer. '''
    return omMPx.asMPxPtr(CurvePointsNode())

def nodeInitializer():

    nAttr = om.MFnNumericAttribute()
    tAttr = om.MFnTypedAttribute()
    eAttr = om.MFnEnumAttribute()
    
    CurvePointsNode.inputCurve = tAttr.create( "inputCurve", "in", om.MFnData.kNurbsCurve)
    tAttr.setConnectable(True)
    
    
    CurvePointsNode.frontAxis = eAttr.create( "frontAxis", "fa", 0)
    eAttr.addField('x',0)
    eAttr.addField('y',1)
    eAttr.addField('z',2)
    eAttr.setStorable(True)
    eAttr.setKeyable(True)
    eAttr.setConnectable(True)
    
    CurvePointsNode.upAxis = eAttr.create( "upAxis", "ua", 1)
    eAttr.addField('x',0)
    eAttr.addField('y',1)
    eAttr.addField('z',2)
    eAttr.setStorable(True)
    eAttr.setKeyable(True)
    eAttr.setConnectable(True)
    
    
   
    CurvePointsNode.upVector = nAttr.create( "upVector", "up", om.MFnNumericData.k3Double)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    
    
    
    CurvePointsNode.twist = nAttr.create( "twist", "twi", om.MFnNumericData.kDouble,0.0)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    

    
    CurvePointsNode.numSample = nAttr.create( "numSample", "ns", om.MFnNumericData.kLong, 1)
    nAttr.setMin(0)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    
    CurvePointsNode.uVal = nAttr.create( "uVal", "u", om.MFnNumericData.kDouble, 0.0)
    nAttr.setArray(True)
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setReadable(True)
    nAttr.setConnectable(True)
    nAttr.setUsesArrayDataBuilder(True)
    

    CurvePointsNode.shift = nAttr.create( "shift", "sh", om.MFnNumericData.kDouble, 0.0 )
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)
    
    CurvePointsNode.isLoop = nAttr.create( "loop", "lp", om.MFnNumericData.kBoolean )
    nAttr.setStorable(True)
    nAttr.setKeyable(True)
    nAttr.setConnectable(True)

    CurvePointsNode.outPositions = nAttr.create("outPositions", "oup", om.MFnNumericData.k3Double)
    nAttr.setArray(True)
    nAttr.setStorable(False)
    nAttr.setHidden(False)
    nAttr.setReadable(True)
    nAttr.setWritable(False)
    nAttr.setUsesArrayDataBuilder(True)
    
    CurvePointsNode.outRotations = nAttr.create("outRotations", "our", om.MFnNumericData.k3Double)
    nAttr.setArray(True)
    nAttr.setStorable(False)
    nAttr.setHidden(False)
    nAttr.setReadable(True)
    nAttr.setWritable(False)
    nAttr.setUsesArrayDataBuilder(True)
    



    CurvePointsNode.addAttribute(CurvePointsNode.inputCurve)
    CurvePointsNode.addAttribute(CurvePointsNode.frontAxis)
    CurvePointsNode.addAttribute(CurvePointsNode.upAxis)
    CurvePointsNode.addAttribute(CurvePointsNode.upVector)
    CurvePointsNode.addAttribute(CurvePointsNode.twist)
    CurvePointsNode.addAttribute(CurvePointsNode.numSample)
    CurvePointsNode.addAttribute(CurvePointsNode.uVal)
    CurvePointsNode.addAttribute(CurvePointsNode.shift)
    CurvePointsNode.addAttribute(CurvePointsNode.isLoop)
    CurvePointsNode.addAttribute(CurvePointsNode.outPositions)
    CurvePointsNode.addAttribute(CurvePointsNode.outRotations)

   

    CurvePointsNode.attributeAffects( CurvePointsNode.inputCurve, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.frontAxis, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.upAxis, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.upVector, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.twist, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.numSample, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.uVal, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.shift, CurvePointsNode.outPositions )
    CurvePointsNode.attributeAffects( CurvePointsNode.isLoop, CurvePointsNode.outPositions )
    
    CurvePointsNode.attributeAffects( CurvePointsNode.inputCurve, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.frontAxis, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.upAxis, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.upVector, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.twist, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.numSample, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.uVal, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.shift, CurvePointsNode.outRotations )
    CurvePointsNode.attributeAffects( CurvePointsNode.isLoop, CurvePointsNode.outRotations )
    


   


def initializePlugin(mobject):
    ''' Initialize the plug-in '''
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write( "Failed to register node: " + kPluginNodeName )
        raise   


def uninitializePlugin( mobject ):
    ''' Uninitializes the plug-in '''
    mplugin = omMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( 'Failed to deregister node: ' + kPluginNodeName )
        raise     
        
    
    

    
    
        
