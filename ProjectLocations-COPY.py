# ---------------------------------------------------------------------------
# ProjectLocations.py
# Kevin Viani 10/21/2014
#
#  This script takes the project locations from warehouse stored on GDB_Assets and turns them into
#  a project location feature class.  
#
# ---------------------------------------------------------------------------

import arcpy
import sys
import os
import smtplib
import datetime
import logging
import logging.handlers
from email.mime.text import MIMEText

errorSent = False


# JOB CONNECTIONS

##connAssets = "D:\\\\SDEConnections\\GDB_Assets(Asset_Admin).sde"
##connGen = "D:\\\\SDEConnections\\GDB_Gen(VTrans_User).sde"
##logfile = "D:\\\\ProjectLocations\\Log\\ProjectLocations.log"

# TEST CONNECTIONS
connAssets = "Database Connections\\GDB_ASSETS.sde"
connGen =  "Database Connections\\GDB_GEN.sde"
logfile = "c:\\Users\\kviani\\Desktop\\ProjectLocations.log"

# WORKING TABLES 
wrkSpc = connAssets 
TBwrkSpc = connAssets

# PROJECT VIEW
ProjVW = connAssets + "\\GDB_Assets.Assets_Admin.VPINS_Projects"

# INPUT GIS FEATURES \ TABLES
LRStwn= connGen+"\\VTRANS_ADMIN.Trans_LRS_Route_twn"
LRSete= connGen+"\\VTRANS_ADMIN.Trans_LRS_Route_ete"

# OUTPUT FEATURE CLASSES
ProjTB = connAssets+ "\\GDB_Assets.Assets_Admin.VPINSProjectsTB"  ##name cannot change
ProjTBname = "VPINSProjectsTB"                                    ##until this variable can be replaced
ProjLoc = connAssets + "\\GDB_Assets.Assets_Admin.VPINS_ProjectsLOC"
CalcBeginPts = connAssets + "\\GDB_Assets.Assets_Admin.VPINS_CalcBeginPTS"

# SETUP LOGGING FILE
logger = logging.getLogger('Project_Logger')
handler = logging.FileHandler(logfile)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info('openning log file')

#SPATIAL REFERENCE
##spRef = arcpy.SpatialReference(4326)
sr = arcpy.SpatialReference(32145)

#ENV VARIABLES
arcpy.env.overwriteOutput =1
arcpy.env.workspace = wrkSpc

#START SCRIPT ---------------------


def prepVIEW ():

    try:
        
        #test to see how many records in the view
        tbCNT = arcpy.GetCount_management(ProjVW)
        print ProjVW + " has: "+ str(tbCNT) + " records"

        #copy the view to a SDE table
        arcpy.TableToTable_conversion (ProjVW, TBwrkSpc, ProjTBname)

        #test to see how many records copy to SDE
        tbCNT = arcpy.GetCount_management(ProjTBname)
        print ProjTBname + " has: "+ str(tbCNT) + " records"

        # add a field to the table that carries location type and set default to NONE
        arcpy.AddField_management(ProjTB, "LocationType", "Text", "", "", "16")
        arcpy.CalculateField_management(ProjTB, "LocationType", '"NONE"')

##        # add a field to the table that carries location type and set default to NONE
##        arcpy.AddField_management(ProjTB, "ErrorType", "Text", "", "", "250")
##        arcpy.CalculateField_management(ProjTB, "ErrorType", '"NONE"')

        ### add a field to the table that carries location type and set default to NONE
        ##arcpy.AddField_management(ProjTB, "CalcBeginMM", "DOUBLE", "16", "3", "")
        ##arcpy.AddField_management(ProjTB, "CalcEndMM", "DOUBLE", "16", "3", "")
        
        
        # add a field to the table that carries location type and set default to NONE
        arcpy.AddField_management(ProjTB, "RecordNumber", "SHORT", "", "")

        rows = arcpy.UpdateCursor(ProjTB) 
        counter = 1
        for row in rows:
            row.RecordNumber = counter
            rows.updateRow(row)
            counter += 1

        print "Table has been prepared"
        
    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)


def convTWNtoETE_SEG():

    try:

        #Create expression that selects projects with begin and end values
        EXPRseg="LRSRoute is not null and BeginETEMileMarker is not null and EndETEMileMarker is not null"
        ##EXPRseg="BeginLRSCode is not null and BeginTownMileMarker is not null and EndLRSCode is not null and EndTownMileMarker is not null "
        ProjTBseg = "VPINS_ProjTBseg"
        arcpy.MakeTableView_management(ProjTB, ProjTBseg, EXPRseg)
        arcpy.CalculateField_management(ProjTBseg,"LocationType",'"SEGMENT"')
        tbCNT2 = arcpy.GetCount_management(ProjTBseg)
        print ProjTBseg + " has: "+ str(tbCNT2) + " records"


##Removed because of FMIS field addition       
##        #Create begin points
##        #Set local variables
##        
##        InputTB = ProjTBseg
##        In_props = "BeginLRSCode POINT BeginTownMileMarker"
##        In_rte = LRStwn 
##        In_rid = "TWN_LR" 
##        New_rte = LRSete 
##        New_rid = "ETE_LR"
##        OutputTB = "VPINSProjTBsegBEG"
##        Out_props = "ETE_RID POINT ETE_FROM_MM"
##        tol = "0.1 meters"
##        Fields= "NO_FIELDS"
##
##        #Create begin points in ETE
##        arcpy.MakeRouteEventLayer_lr(In_rte, In_rid, ProjTBseg, In_props, OutputTB)
##        arcpy.LocateFeaturesAlongRoutes_lr(OutputTB, New_rte, New_rid, tol, "VPINSProjTBsegBEGete", "ETE_RID POINT ETE_FROM_MM")
##
##        arcpy.MakeTableView_management(ProjTB, "ProjTBview")        
##        arcpy.MakeTableView_management("VPINSProjTBsegBEGete", "BegPTS")
##        fields= ["ETE_RID", "ETE_FROM_MM"]      
##        arcpy.JoinField_management("ProjTBview", "RecordNumber", "BegPTS", "RecordNumber", fields)
##
##        #Create end points
##        # Set local variables
##        
##        InputTB = ProjTBseg
##        In_props = "EndLRSCode POINT EndTownMileMarker"
##        In_rte = LRStwn 
##        In_rid = "TWN_LR" 
##        New_rte = LRSete 
##        New_rid = "ETE_LR"
##        OutputTB = "VPINSProjTBsegEND"
##        Out_props = "ETE_RID POINT ETE_TO_MM"
##        tol = "0.1 meters"
##        Fields= "NO_FIELDS"
##
##        #Create end points in ETE
##        arcpy.MakeRouteEventLayer_lr(In_rte, In_rid, ProjTBseg, In_props, OutputTB)
##        arcpy.LocateFeaturesAlongRoutes_lr(OutputTB, New_rte, New_rid, tol, "VPINSProjTBsegENDete", "ETE_RID POINT ETE_TO_MM")
##
##        arcpy.MakeTableView_management(ProjTB, "ProjTBview")        
##        arcpy.MakeTableView_management("VPINSProjTBsegENDete", "EndPTS")
##        fields= ["ETE_RID", "ETE_TO_MM"]
##        arcpy.JoinField_management("ProjTBview", "RecordNumber", "EndPTS", "RecordNumber", fields)
##              

        #Create expression that selects projects with begin and end values
        EXPRseg="LRSRoute is not null and BeginETEMileMarker is not null and EndETEMileMarker is not null"
        ##EXPRseg="BeginLRSCode is not null and BeginTownMileMarker is not null and EndLRSCode is not null and EndTownMileMarker is not null "
        ProjTBseg = "VPINS_ProjTBseg"
        arcpy.MakeTableView_management(ProjTB, ProjTBseg, EXPRseg)
        arcpy.CalculateField_management(ProjTBseg,"LocationType",'"SEGMENT"')
        tbCNT2 = arcpy.GetCount_management(ProjTBseg)
        print ProjTBseg + " has: "+ str(tbCNT2) + " records"

        #Create Final Segments
        #Set local variables

##        ProjTBfullSeg = "VPINS_ProjTBfullSeg"
##        EXPRfullSeg="LocationType = 'SEGMENT'"
##        arcpy.MakeTableView_management(ProjTB, ProjTBfullSeg, EXPRfullSeg)
        In_props = "LRSRoute LINE BeginETEMileMarker EndETEMileMarker"
        Route_rte = LRSete 
        Route_rid = "ETE_LR"
        OutputFC = "VPINS_Project_Segments"

        arcpy.MakeRouteEventLayer_lr(Route_rte, Route_rid, ProjTBseg, In_props, "VPINS_SegmentsVW")
        arcpy.CopyFeatures_management ("VPINS_SegmentsVW", OutputFC)
                
        #test to see how many records in the view
        tbCNT = arcpy.GetCount_management(OutputFC)
        print OutputFC + " has: "+ str(tbCNT) + " records"


    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)

def CreateLRSPoints():

    try:

        #Create expression that selects projects where beg and end values are equal and there is a LRS value

       ## EXPRpts="BeginTownMileMarker=EndTownMileMarker and BeginLRSCode is not null"
        EXPRpts="LRSRoute is not null and BeginETEMileMarker=EndETEMileMarker"
        ProjTBpts = "VPINS_ProjTBpts"
        arcpy.MakeTableView_management(ProjTB, ProjTBpts, EXPRpts)
        arcpy.CalculateField_management(ProjTBpts,"LocationType",'"LRSPOINT"')
        tbCNT = arcpy.GetCount_management(ProjTBpts)
        print ProjTBpts + " has: "+ str(tbCNT) + " records"
        
        #Create LRS points
        #Set local variables

        InputTB = ProjTBpts
        In_props = "LRSRoute POINT BeginETEMileMarker"
        In_rte = LRSete 
        In_rid = "ETE_LR"
        OutputTB = "VPINSProjTBptsLRS"
        OutputFC_lrs = "VPINS_PtsLRS"

        #Create points
        arcpy.MakeRouteEventLayer_lr(In_rte, In_rid, ProjTBpts, In_props, OutputTB)
        arcpy.CopyFeatures_management (OutputTB, OutputFC_lrs)

        return (OutputFC_lrs)

    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)


def CreateXYPoints():

    try:

        #Create expression that selects projects with northing and easting
        EXPRptsXY="Northing is not null and LocationType = 'NONE'"
        ProjTBptsXY = "VPINS_ProjTBptsXY"
        arcpy.MakeTableView_management(ProjTB, ProjTBptsXY, EXPRptsXY)
        arcpy.CalculateField_management(ProjTBptsXY,"LocationType",'"XYPOINT"')

        tbCNT = arcpy.GetCount_management(ProjTBptsXY)
        print ProjTBptsXY + " has: "+ str(tbCNT) + " records"

        #shouldn't need this but I can't get the selection to work right
        EXPRptsXY2="LocationType='XYPOINT'"
        ProjTBptsXY2 = "VPINS_ProjTBptsXY2"
        arcpy.MakeTableView_management(ProjTB, ProjTBptsXY2, EXPRptsXY2)

        tbCNT = arcpy.GetCount_management(ProjTBptsXY2)
        print ProjTBptsXY2 + " has: "+ str(tbCNT) + " records"

        #create an xy layer from the data
        table = ProjTBptsXY2
        in_x_field = "Easting"
        in_y_field = "Northing"
        out_layer = "VPINS_Proj_XY"
        spatial_reference = sr
        OutputFC_xy = "VPINS_PtsXY"
        whereXY="LocationType='XYPOINT'"

        arcpy.MakeXYEventLayer_management (table, in_x_field, in_y_field, out_layer, spatial_reference)
        arcpy.MakeFeatureLayer_management (out_layer, "ProjXYposs", whereXY)
        arcpy.CopyFeatures_management ("ProjXYposs", OutputFC_xy)
        
        tbCNT = arcpy.GetCount_management(OutputFC_xy)
        print OutputFC_xy + " has: "+ str(tbCNT) + " records"

        return (OutputFC_xy)

         
    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)


def EmptyTable():

    try:
        ProjTBnoLocFinal= "VPINS_Projects_NoLoc" 
        EXPRnoLoc="LocationType = 'NONE'"
        ProjTBnoLoc = "VPINS_ProjTBnoLoc"
        arcpy.MakeTableView_management(ProjTB, ProjTBnoLoc, EXPRnoLoc)
        arcpy.Merge_management (ProjTBnoLoc, ProjTBnoLocFinal)

        ##arcpy.DeleteFeatures_management (ProjTB)
         
    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)


def MergePointData(XY,LRS):

    try:
        ptLayers=[XY,LRS]
        output= "VPINS_Project_Points"
        arcpy.Merge_management (ptLayers, output)

        arcpy.DeleteFeatures_management(XY)
        arcpy.DeleteFeatures_management(LRS)
        
    except Exception, msg:
        logger.error(msg)
        if not errorSent:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(fname, exc_tb.tb_lineno, msg)
            sendError(exc_tb.tb_lineno, msg)



def sendError(lineNo, msg):
    body = 'The python script Project Locations on line ' + str(lineNo) +  ' with the following error:  ' + str(msg)
    fromaddr = 'kevin.viani@state.vt.us'
    toaddrs = 'kevin.viani@state.vt.us'
    content = MIMEText(body)
    content['Subject'] = 'Python Script Failure:  Project Locations'
    content['From'] =  fromaddr
    ##content['To'] =  ", ".join(toaddrs)
    server = smtplib.SMTP('relay.state.vt.us')
    server.sendmail(fromaddr, toaddrs, content.as_string())
    server.quit()
    errorSent = True
    logger.error('Failed on line ' + str(lineNo) + str(msg))      



def main ():

    try:
        prepVIEW ()
        convTWNtoETE_SEG()
        LRS=CreateLRSPoints()
        XY=CreateXYPoints()
        MergePointData(XY,LRS)
        EmptyTable()
    
    except Exception, msg:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
        print(fname, exc_tb.tb_lineno, msg)
        logger.error(fname, exc_tb.tb_lineno, msg)
        if not errorSent:
            sendError(exc_tb.tb_lineno, msg)
   
    finally:

        del XY
        del LRS
        
        print "SCRIPT COMPLETE"
        logger.info("Script Complete")
        logging.shutdown()
                    
if __name__ == "__main__":
    main() 