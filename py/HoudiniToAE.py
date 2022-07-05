# HDA available at https://github.com/furlfurlfurl/HoudiniToAE
# Inspired by moam1986's Houdini_2_AE (https://www.orbolt.com/asset/moam1986::houdini_2_ae)

# New functionality:
## Simple HDA
## Possible to undo the import
## Export points (position and pscale)
## Much faster AE import

# This function basically writes the .jsx from top to bottom,
# exception being that it builds the animation part separately and adds it at the end
def export_params(kwargs):

    # Get parent node
    parent = kwargs['node']
    
    # Initiate jsx vars
    jsx = ""
    ani = ""
    curTime = hou.time()
    rotation_order = "xyz"
    lb = "\n"
    tb = "  "
    
    # Get parms from node
    param_nulls = parent.parm('data_objects').eval()
    #frame_start = parent.parm('param_startframe').eval()
    #frame_end = parent.parm('param_endframe').eval()
    frame_start = parent.parmTuple('param_startend').eval()[0]
    frame_end = parent.parmTuple('param_startend').eval()[1]
    uniform_scale = parent.parm('param_uniformscale').eval()
    param_points = parent.parm('data_points').eval()
    param_camera = parent.parm('data_camera').eval()
    param_pscaleattribute = parent.parm('param_pscaleattribute').eval()
    param_orientattribute = parent.parm('param_orientattribute').eval()
    param_compname = parent.parm('param_compname').eval()
        
    ## .jsx comp
    jsx += "// Allow undo" + lb
    jsx += "app.beginUndoGroup('Import Houdini Scene')" + lb
    
    jsx += lb + "// Comp" + lb
    jsx += "var comp = app.project" + lb
    jsx += "var items = comp.items" + lb
    jsx += "var composition_name = \'" + param_compname + "\'" + lb
    
    # Need to get the camera early for the resolution
    node_camera = hou.node(param_camera)
    resolution = node_camera.parmTuple("res").eval()
    
    jsx += "var composition_aspect = 1" + lb
    jsx += "var composition_resolution_x = " + str(resolution[0]) + "" + lb
    jsx += "var composition_resolution_y = " + str(resolution[1]) + "" + lb
    jsx += "var composition_fps = " + str(hou.fps()) + "" + lb
    jsx += "var composition_frames = " + str(frame_end - frame_start + 1) + "" + lb
    jsx += "var composition_time = composition_frames/composition_fps" + lb
    jsx += "var composition = items.addComp(composition_name,composition_resolution_x,composition_resolution_y,composition_aspect,composition_time,composition_fps)" + lb

    
    
    
    ## .jsx main camera
    jsx += lb + "// Camera" + lb       

    var_name = node_camera.name()
    jsx += "var " + var_name + " = composition.layers.addCamera(\'" + var_name + "\',[0,0])" + lb
    #jsx += var_name + ".name = \'" + var_name + "\'" + lb
    jsx += var_name + ".property(\'Point of Interest\').expression=\'transform.position\'" + lb
    
    # Position
    jsx += "var " + var_name + "_positions = " + str(get_obj_translates(node_camera, uniform_scale, frame_start, frame_end)) + "" + lb
    #ani += var_name + ".property(\'Position\').setValueAtTime(i/composition_fps, " + var_name + "_positions[i])" + lb
    ani += var_name + ".property(\'Position\').setValuesAtTimes(times, " + var_name + "_positions)" + lb
    
    # Rotation   
    jsx += "var " + var_name + "_rotationsX = " + str(get_obj_rotations_specific(node_camera, "x", frame_start, frame_end)) + "" + lb
    jsx += "var " + var_name + "_rotationsY = " + str(get_obj_rotations_specific(node_camera, "y", frame_start, frame_end)) + "" + lb
    jsx += "var " + var_name + "_rotationsZ = " + str(get_obj_rotations_specific(node_camera, "z", frame_start, frame_end)) + "" + lb
    ani += var_name + ".property(\'X Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsX)" + lb
    ani += var_name + ".property(\'Y Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsY)" + lb
    ani += var_name + ".property(\'Z Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsZ)" + lb
    
    # Zoom
    jsx += "var " + var_name + "_zooms = " + str(get_cam_zooms(node_camera, frame_start, frame_end)) + "" + lb
    ani += var_name + ".property(\'Zoom\').setValuesAtTimes(times, " + var_name + "_zooms)" + lb
    
    # Focus
    jsx += "var " + var_name + "_focuses = " + str(get_cam_focuses(node_camera, uniform_scale, frame_start, frame_end)) + "" + lb
    ani += var_name + ".property(\'Focus Distance\').setValuesAtTimes(times, " + var_name + "_focuses)" + lb
    
    ani += lb
    
    
    
    ## .jsx objects
    jsx += lb + "// Objects"
    for objPath in param_nulls.split():
        jsx += lb
        
        # Prepare this locator's info
        node = hou.node(objPath)
        var_name = node.name()
        
        # Create the null and name it
        jsx += "var " + var_name + " = composition.layers.addNull()" + lb
        jsx += var_name + ".name = \'" + var_name + "\'" + lb
        jsx += var_name + ".threeDLayer = 1" + lb
        jsx += var_name + ".label = 1" + lb
        
        # Location       
        jsx += "var " + var_name + "_positions = " + str(get_obj_translates(node, uniform_scale, frame_start, frame_end)) + "" + lb
        ani += var_name + ".property(\'Position\').setValuesAtTimes(times, " + var_name + "_positions)" + lb
        
        # Rotation       
        jsx += "var " + var_name + "_rotationsX = " + str(get_obj_rotations_specific(node, "x", frame_start, frame_end)) + "" + lb
        jsx += "var " + var_name + "_rotationsY = " + str(get_obj_rotations_specific(node, "y", frame_start, frame_end)) + "" + lb
        jsx += "var " + var_name + "_rotationsZ = " + str(get_obj_rotations_specific(node, "z", frame_start, frame_end)) + "" + lb
        ani += var_name + ".property(\'X Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsX)" + lb
        ani += var_name + ".property(\'Y Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsY)" + lb
        ani += var_name + ".property(\'Z Rotation\').setValuesAtTimes(times, " + var_name + "_rotationsZ)" + lb
                
        # Scale
        #jsx += "var " + var_name + "_scales = " + str(get_obj_scales(node, uniform_scale, frame_start, frame_end)) + "" + lb
        #ani += var_name + ".property(\'Scale\').setValueAtTime(i/composition_fps, " + var_name + "_scales[i])" + lb
        
        jsx += "var " + var_name + "_scales = " + str(get_obj_scales(node, uniform_scale, frame_start, frame_end)) + "" + lb
        ani += var_name + ".property(\'Scale\').setValuesAtTimes(times, " + var_name + "_scales)" + lb

        ani += lb
        
        
        
    ## .jsx points
    jsx += lb + "// Points"
    for objPath in param_points.split():
        node = hou.node(objPath)
        for point in node.geometry().points():
            jsx += lb
            
            # Prepare this point's info

            var_name = node.name() + "_" + str(point.number())
            
            # Create the null and name it
            jsx += "var " + var_name + " = composition.layers.addNull()" + lb
            jsx += var_name + ".name = \'" + var_name + "\'" + lb
            jsx += var_name + ".threeDLayer = 1" + lb
            jsx += var_name + ".label = 2" + lb
            
            # Position
            jsx += "var " + var_name + "_positions = " + str(get_point_translates(point, uniform_scale, frame_start, frame_end)) + "" + lb
            #ani += var_name + ".property(\'Position\').setValueAtTime(i/composition_fps, " + var_name + "_positions[i])" + lb
            ani += var_name + ".property(\'Position\').setValuesAtTimes(times, " + var_name + "_positions)" + lb
                     
            # Rotation (wonky due to how to quat data is  handled)
            #if param_orientattribute:
            #    jsx += "var " + var_name + "_rotations = " + str(get_point_rotates(point, param_orientattribute, frame_start, frame_end)) + "" + lb
            #    ani += "    " + var_name + ".property(\'X Rotation\').setValueAtTime(i/composition_fps, " + var_name + "_rotations[i][0])" + lb
            #    ani += "    " + var_name + ".property(\'Y Rotation\').setValueAtTime(i/composition_fps, " + var_name + "_rotations[i][1])" + lb
            #    ani += "    " + var_name + ".property(\'Z Rotation\').setValueAtTime(i/composition_fps, " + var_name + "_rotations[i][2])" + lb
            
            # Scale
            if param_pscaleattribute:
                jsx += "var " + var_name + "_scales = " + str(get_point_scales(point, param_pscaleattribute, uniform_scale, frame_start, frame_end)) + "" + lb
                #ani += var_name + ".property(\'Scale\').setValueAtTime(i/composition_fps, " + var_name + "_scales[i])" + lb
                ani += var_name + ".property(\'Scale\').setValuesAtTimes(times, " + var_name + "_scales)" + lb
                
            ani += lb
        
        
        
    ## .jsx animation
    jsx += lb + "// Animation" + lb
    jsx += "times = []" + lb
    jsx += "for(var i=0; i < composition_frames; i++){ times.push(i/composition_fps) }" + lb + lb
    jsx += ani.rstrip()
    
    # Clean up
    hou.setTime(curTime)
    
    # Save the file
    jsx += lb + lb + "app.endUndoGroup()"
    export_lines(jsx, parent.parm('param_filepath').eval())
        
    
#####################################################

def export_lines(lines, path):
    f = open(path, 'w')
    f.writelines(lines)
    f.close()

def get_point_location(node, id):
    return node.displayNode().geometry().point(id).position()


def get_point_translates(point, uniformScale, startFrame, endFrame):
    translates = []
    for i in range(startFrame, endFrame+1):
        hou.setTime((i-1)/hou.fps())
        position = point.position()
        translate = [round(position[0] * uniformScale, 4), round(position[1] * uniformScale * -1, 4), round(position[2] * uniformScale * -1, 4)]
        translates.append(translate)
    return translates

# ! Returns incompatible rotation order
#def get_point_rotates(point, attributeName, startFrame, endFrame):
#    rotates = []
#    for i in range(startFrame, endFrame+1):
#        hou.setTime((i-1)/hou.fps())
#        quat = hou.Quaternion(point.attribValue(attributeName))
#        euler = quat.extractEulerRotates("zyx")
#        rotation = [round(euler[0], 4), round(euler[1] * -1, 4), round(euler[2] * -1, 4)]
#        rotates.append(rotation)
#    return rotates

def get_point_scales(point, attributeName, uniformScale, startFrame, endFrame):
    rotates = []
    for i in range(startFrame, endFrame+1):
        hou.setTime((i-1)/hou.fps())
        attrib = point.attribValue(attributeName)
        rotation = [round(attrib[0] * uniformScale * 100, 4), round(attrib[1] * uniformScale * -100, 4), round(attrib[2] * uniformScale * -100, 4)]
        rotates.append(rotation)
    return rotates
    
def get_obj_translates(node, uniformScale, startFrame, endFrame):  
    translates = []
    for i in range(startFrame, endFrame+1):
        time = (i-1)/hou.fps()
        transform = node.worldTransformAtTime(time)
        attrib = transform.extractTranslates()
        translate = [round(attrib[0] * uniformScale, 4), round(attrib[1] * uniformScale * -1, 4), round(attrib[2] * uniformScale * -1, 4)]
        translates.append(translate)
    return translates
    
#def get_obj_rotations(objNode, startFrame, endFrame):  
#    rotations = []
#    for i in range(startFrame, endFrame+1):
#        time = (i-1)/hou.fps()
#        transform = objNode.worldTransformAtTime(time)
#        attrib = transform.extractRotates(rotate_order="xyz")
#        rotation = [round(attrib[0], 4), round(attrib[1] * -1, 4), round(attrib[2] * -1, 4)]
#        rotations.append(rotation)
#    return rotations

def get_obj_rotations_specific(objNode, dimension, startFrame, endFrame):  
    rotations = []
    for i in range(startFrame, endFrame+1):
        time = (i-1)/hou.fps()
        transform = objNode.worldTransformAtTime(time)
        rotation_order = "zyx"
        attrib = transform.extractRotates(rotate_order=rotation_order)
        
        if dimension == 'x':
            rotations.append(round(attrib[0], 4))
        
        if dimension == 'y':
            rotations.append(round(attrib[1] * -1, 4))
            
        if dimension == 'z':
            rotations.append(round(attrib[2] * -1, 4))

    return rotations
    
def get_obj_scales(objNode, uniformScale, startFrame, endFrame):  
    scales=[]
    for i in range(startFrame, endFrame+1):
        time = (i-1)/hou.fps()
        transform = objNode.worldTransformAtTime(time)
        scale=[round(transform.extractScales()[0]*uniformScale*100,4), round(transform.extractScales()[1]*uniformScale*100,4), round(transform.extractScales()[2]*uniformScale*100,4)]
        scales.append(scale)
    return scales
    
def get_cam_zooms(cameraNode, startFrame, endFrame):
    node_camera_parm_aperture = cameraNode.parm("aperture")
    node_camera_parm_focal = cameraNode.parm("focal")
    node_camera_parm_aspect = cameraNode.parm("aspect")
    node_camera_parm_res = cameraNode.parmTuple("res")
    
    zooms = []
    for i in range(startFrame, endFrame + 1):
        time = (i-1)/hou.fps()
        aperture = node_camera_parm_aperture.evalAtTime(time)
        focal = node_camera_parm_focal.evalAtTime(time)
        aspect = node_camera_parm_aspect.evalAtTime(time)
        resx = node_camera_parm_res.evalAsInts()[0]
        resy = node_camera_parm_res.evalAsInts()[1]
        angle = extract_camera_zoom(cameraNode, aperture, focal, aspect, resx, resy)
        zooms.append(round(angle,4))
        
    return zooms

def extract_camera_zoom(cameraNode, aperture, focal, aspect, resx, resy):
    node_hda_parm_camera_keys = cameraNode.parm("camera_keys")

    cam_aspect = (float(resy)/float(resx))*(1/aspect)
    sensor_size_x = aperture
    sensor_size_y = aperture * cam_aspect
    zoom = focal*resx/sensor_size_x/cam_aspect
    zoom = focal*resx/sensor_size_y*cam_aspect
    return zoom

def get_cam_focuses(cameraNode, uniformScale, startFrame, endFrame):
    node_camera_parm_focus = cameraNode.parm("focus")
    
    focuses = []
    for i in range(startFrame, endFrame + 1):
        time = (i-1)/hou.fps()
        focus = node_camera_parm_focus.evalAtTime(time) * uniformScale
        focuses.append(round(focus,4))
        
    return focuses