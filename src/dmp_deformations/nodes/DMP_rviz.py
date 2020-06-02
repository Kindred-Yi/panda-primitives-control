#!/usr/bin/env python

""" Calculates DMP using LWR
 Created: 02/19/2020
"""

__author__ = "Mike Hagenow"

import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt
import mayavi.mlab as mlab
import os
import rospy
from DMP import DMP
from scipy import signal
from std_msgs.msg import String
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import MarkerArray, Marker
import csv
from dtw import dtw
import PyBSpline


demonstrations = []

pathDMP = None
forceDMP = None
path0 = None
path1 = None
path2 = None
path3 = None
path4 = None

def getSegmentation(demo):
    # Go through demonstration and look for contact, un-contact events
    # The data has been downsampled to 50 Hz
    number_samples_contact = 10
    number_samples_not_contact = 10
    force_threshold = 5.0

    states = []

    in_contact = False
    states.append((0,np.array([1, 1, 1])))

    # print "LENGTH"
    # print np.shape(demo)

    # 2nd order filter
    b, a = signal.butter(2, 1.0,fs=50)
    y = signal.filtfilt(b, a, np.linalg.norm(demo[:,3:],axis=1), padlen=0)
    y = y-np.min(y)
    # import matplotlib.pyplot as plt
    # plt.plot(np.linalg.norm(demo[:,3:],axis=1))
    # plt.plot(y)
    # plt.show()

    for ii in range(1,len(demo)):
        # Add the position control event
        if not in_contact and np.all(y[ii:ii+number_samples_contact]>force_threshold):
            states.append((ii,np.array([1, 1, 0])))
            in_contact = True
        # Add the force start control event
        if in_contact and np.all(y[ii:ii+number_samples_not_contact]<force_threshold): # and norm whatever
            states.append((ii,np.array([1, 1, 1])))
            # add constraint frame eventually
            in_contact = False

    return states


def plot_paths_rviz(demonstration_data_trimmed,trajectories):
    global path0, path1, path2, path3, path4, pathDMP, forceDMP
    # Clear all existing in RVIZ
    emptyPath = Path()
    emptyPath.header.frame_id = 'base_link'
    emptyPath.header.stamp = rospy.Time.now()
    pathDMP.publish(emptyPath)
    path0.publish(emptyPath)
    path1.publish(emptyPath)
    path2.publish(emptyPath)
    path3.publish(emptyPath)
    path4.publish(emptyPath)
    emptyForces = MarkerArray()
    forceDMP.publish(emptyForces)

    for ii in range(0,len(demonstration_data_trimmed)):
        demo = demonstration_data_trimmed[ii]
        tempPath = Path()
        tempPath.header.frame_id = 'base_link'
        tempPath.header.stamp = rospy.Time.now()
        for jj in range(0,np.shape(demo)[0]):
            tempPose = PoseStamped()
            tempPose.header.stamp = rospy.Time.now()
            tempPose.pose.position.x = demo[jj,0]
            tempPose.pose.position.y = demo[jj,1]
            tempPose.pose.position.z = demo[jj,2]
            tempPose.pose.orientation.x = 0.0
            tempPose.pose.orientation.y = 0.0
            tempPose.pose.orientation.z = 0.0
            tempPose.pose.orientation.w = 1.0
            tempPath.poses.append(tempPose)
    
        # Publish the original paths
        if ii==0:
            path0.publish(tempPath)
        elif ii==1:
            path1.publish(tempPath)
        elif ii==2:
            path2.publish(tempPath)
        elif ii==3:
            path3.publish(tempPath)
        else:
            # If more than 5 paths, just update last
            path4.publish(tempPath)

        # Publish the DMP
        tempPath = Path()
        tempPath.header.frame_id = 'base_link'
        tempPath.header.stamp = rospy.Time.now()

        tempForces = MarkerArray()
        for jj in range(0,len(trajectories[0])):
            tempPose = PoseStamped()
            tempPose.header.stamp = rospy.Time.now()
            tempPose.pose.position.x = trajectories[0][jj]
            tempPose.pose.position.y = trajectories[1][jj]
            tempPose.pose.position.z = trajectories[2][jj]
            tempPose.pose.orientation.x = 0.0
            tempPose.pose.orientation.y = 0.0
            tempPose.pose.orientation.z = 0.0
            tempPose.pose.orientation.w = 1.0
            tempPath.poses.append(tempPose)

            tempForce = Marker()
            tempForce.color.a = 1.0
            tempForce.color.r = 1.0
            tempForce.color.b = 0.0
            tempForce.color.g = 0.0
            
            if jj % 10 == 0:
                # TODO STILL ONLY WORKS FOR FORCES IN THE Z-DIRECTION
                tempForce.pose.position.x = trajectories[0][jj]
                tempForce.pose.position.y = trajectories[1][jj]
                tempForce.pose.position.z = trajectories[2][jj]
                tempForce.pose.orientation.x = 0.0
                tempForce.pose.orientation.y = 0.7068
                tempForce.pose.orientation.z = 0.0
                tempForce.pose.orientation.w = 0.7074
                tempForce.header.frame_id = "base_link"
                tempForce.header.stamp = rospy.Time.now()
                tempForce.id = jj
                tempForce.type = Marker.ARROW
                tempForce.action = Marker.ADD
                tempForce.scale.x = -trajectories[5][jj]/300
                tempForce.scale.y = 0.003
                tempForce.scale.z = 0.003
                tempForces.markers.append(tempForce)


        forceDMP.publish(tempForces)
        pathDMP.publish(tempPath)
        # print "Pushing Data to RVIZ" 


def resetDMP(data):
    global demonstrations
    demonstrations = []
    global path0, path1, path2, path3, path4, pathDMP, forceDMP
    # Clear all existing in RVIZ
    emptyPath = Path()
    emptyPath.header.frame_id = 'base_link'
    emptyPath.header.stamp = rospy.Time.now()
    pathDMP.publish(emptyPath)
    path0.publish(emptyPath)
    path1.publish(emptyPath)
    path2.publish(emptyPath)
    path3.publish(emptyPath)
    path4.publish(emptyPath)
    emptyForces = MarkerArray()
    emptyMarker = Marker()
    emptyMarker.action = Marker.DELETEALL
    emptyForces.markers.append(emptyMarker)
    forceDMP.publish(emptyForces)

def loadPresegmentedCore(file):
    directory = '/home/mike/Documents/MikePanda/devel/lib/dmp_deformations'
    demonstration_data = []

    # Skip over lines for surfaces, segmentation samples, interaction, and variance
    demonstration_data.append(np.loadtxt(directory+'/'+file, delimiter=",", skiprows=4))
    segmentation = []

    # Zip doesn't work if there is 1 entry since it is not iterable
    if(np.shape(np.loadtxt(directory+'/'+file, delimiter=",",max_rows=1,skiprows=1))!=()):
        for surface_model,point,interaction,const_variance in zip(np.genfromtxt(directory+'/'+file,delimiter=",",max_rows=1,dtype='str') ,np.loadtxt(directory+'/'+file, delimiter=",",max_rows=1, skiprows=1),np.loadtxt(directory+'/'+file, delimiter=",",max_rows=1, skiprows=2),np.genfromtxt(directory+'/'+file,delimiter=",",max_rows=1,skip_header=3,dtype='str')):
            # right now only allows for position-level

            temp_var = np.array(const_variance.split(" "))

            if interaction==1:
                # TODO: fix this!!!!
                segmentation.append((point, temp_var, np.array([1, 1, 1, 1, 1, 1, 1]),surface_model))
            else:
                segmentation.append((point, temp_var, np.array([1, 1, 0, 1, 1, 1, 1]),surface_model))
    else:
        surface_model = np.genfromtxt(directory+'/'+file,delimiter=",",max_rows=1,dtype='str')
        point = np.loadtxt(directory+'/'+file, delimiter=",",max_rows=1, skiprows=1)
        interaction = np.loadtxt(directory+'/'+file, delimiter=",",max_rows=1, skiprows=2)
        if interaction == 1:
            # TODO: fix this!!!!
            segmentation.append((point, np.array([1, 1, 1, 1, 1, 1, 1]),surface_model))
        else:
            segmentation.append((point, np.array([1, 1, 0, 1, 1, 1, 1]),surface_model))

    calculateDMP(demonstration_data, segmentation)
    print "..."
    print "..."
    print "LOAD AND CALCULATIONS COMPLETE"


def loadPresegmented(data):
    loadPresegmentedCore(data.data)


def loadData(data):
    global demonstrations
    # File structure is a list of arrays (one per demonstration)
    # Each array is an n-samples by 6 array for the 3 positions and 3 forces
    print ""
    print ""
    print ""
    print("Loading Data from CSV")

    #TODO: Get directory from ros path
    directory = '/home/mike/Documents/MikePanda/devel/lib/dmp_deformations'
    
    demonstrations.append(data.data)
    demonstration_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".csv") and filename in demonstrations:
            print("Loading File: " + filename)
            demonstration_data.append(np.loadtxt(open(directory + '/' + filename, "rb"), delimiter=",", skiprows=0)[0:-1:20])

    # Segmentation is calculated from the first demonstration
    # Done here so that calculateDMP can also be called
    # with a predetermined segmentation
    # This will figure out how many DMPs are needed to encode
    # the motion
    segmentation = getSegmentation(demonstration_data[0])

    print "SEGMENTATION:",len(segmentation)
    print segmentation
    # print "Number of Contacts: ",(len(segmentation)-1)/2
    calculateDMP(demonstration_data, segmentation)
    print "LOAD AND CALCULATIONS COMPLETE"


def calculateDMP(demonstration_data, segmentation):
    print "Building DMPs"
    dmps = []

    # Use Dynamic Time Warping to figure out the equivalent
    # index scaling for each of the additional demonstrations

    # DTW is just done with the x,y,and z-values for now
    # only relevant anyways when doing LFD with multiple demonstrations

    x = []
    for ii in range(0,np.shape(demonstration_data[0])[0]):
        # Features are stored as lists of tuples
        x.append((demonstration_data[0][ii,0],demonstration_data[0][ii,1],demonstration_data[0][ii,2]))

    alignment_curves = []
    for ii in range(0,len(demonstration_data)):
        y = []
        # compare each of the demos to the first which is used for segmentation
        manhattan_distance = lambda x, y: np.abs(x[0] - y[0])+np.abs(x[1] - y[1])+np.abs(x[2] - y[2])

        for jj in range(0, np.shape(demonstration_data[ii])[0]):
            # Features are stored as lists of tuples
            y.append((demonstration_data[ii][jj, 0], demonstration_data[ii][jj, 1], demonstration_data[ii][jj, 2]))

        d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=manhattan_distance)
        alignment_curves.append((path[0],path[1]))


    # Write a CSV with the final trajectory which can be read and executed
    with open('/home/mike/Documents/MikePanda/devel/lib/dmp_deformations/learneddmp.csv', 'w') as csvfile:
        # Write to file for potential replay
        # print "Writing to DMP file"

        demonstration_data_trimmed = []
        trajectories_plotting=[]

        # For each of the DMPs
        for xx in range(0,len(segmentation)):
            segment = segmentation[xx]

            # Create a DMP
            dmp = DMP()
            dmps.append(dmp)

            sel_vec = segment[2]
            variances = segment[1]

            demonstration_per_dmp = []
            
            # Get the DMP sections for each of the demonstrations
            for yy in range(0,len(demonstration_data)):
                demo = demonstration_data[yy]

                 # Get Start and End Points
                start_index = segment[0]
                start_index = alignment_curves[yy][1][int(np.round(np.median(np.where(alignment_curves[yy][0]==start_index))))]
                end_index = len(demo)

                # print "LEN:",np.shape(demo)

                # If not the last segment, get the next event index
                if xx+1<len(segmentation):
                    end_index = segmentation[xx+1][0]
                    end_index = alignment_curves[yy][1][
                        int(np.round(np.median(np.where(alignment_curves[yy][0] == end_index))))]

                    
                temp = np.zeros((end_index-start_index,7))
                # Get either forces or positions depending on selection vector
                # First three are positions, 7-9 are forces (after quaternion)
                temp[:, 0] = demo[start_index:end_index,0+7*(1-sel_vec[0])].reshape((end_index-start_index,))
                temp[:, 1] = demo[start_index:end_index,1+7*(1-sel_vec[1])].reshape((end_index-start_index,))
                temp[:, 2] = demo[start_index:end_index,2+7*(1-sel_vec[2])].reshape((end_index-start_index,))
                temp[:, 3] = demo[start_index:end_index,3].reshape((end_index - start_index,))
                temp[:, 4] = demo[start_index:end_index,4].reshape((end_index - start_index,))
                temp[:, 5] = demo[start_index:end_index,5].reshape((end_index - start_index,))
                temp[:, 6] = demo[start_index:end_index,6].reshape((end_index - start_index,))

                # Positions for plotting
                temp_pos = np.zeros((end_index-start_index,3))

                # Get either forces or positions depending on selection vector
                # First three are positions, second three are forces
                temp_pos[:,:] = demo[start_index:end_index,0:3].reshape((end_index-start_index,3))
                
                demonstration_per_dmp.append(temp)

                # # Just for plotting
                # if len(demonstration_data_trimmed)<(yy+1):
                #     demonstration_data_trimmed.append(temp_pos)
                # else:
                #     demonstration_data_trimmed[yy] = np.append(demonstration_data_trimmed[yy],temp_pos,axis=0)

            dmps[xx].inputData(demonstration_data=demonstration_per_dmp)
            dmps[xx].computeDMP()

            
            trajectories = dmps[xx].getTrajectory()
            zero_length = len(trajectories[0])
            print "ZERO LENGTH: ",zero_length


            # Figure out how long the demonstration should be based on max difference (velocity)
            # in kinematic directions and interpolate such that this is sent at 1000 Hz.

            #########################################################################
            # Determine the playback speed based on velocities in the demonstration #
            #########################################################################

            max_vel = 0.15 # m/s
            panda_delta_T = 0.01 # 1 ms # TODO: MOVE TO CONFIG!
            # TODO: this really should probably be switched back to maximum velocity

            if sel_vec[2]==1: # Position control
                max_x = sel_vec[0]*np.average(np.diff(np.array(trajectories[0]),axis=0))
                max_y = sel_vec[1]*np.average(np.diff(np.array(trajectories[1]),axis=0))
                max_z = sel_vec[2]*np.average(np.diff(np.array(trajectories[2]),axis=0))
                average_vel = np.sqrt(np.power(max_x, 2) + np.power(max_y, 2) + np.power(max_z, 2))
            else: # hybrid control
                surfaceModel = PyBSpline.BSplineSurface()
                surfaceModel.loadSurface("curved")

                # x and y are the surface parameters
                # need to get the actual 3D points from the Spline Suface

                points_3d = []

                # 10x downsampling for performance
                downsample = 10
                count = 0
                for traj_x,traj_y in zip(trajectories[0],trajectories[1]):
                    if count%downsample==0:
                        points_3d.append(surfaceModel.calculate_surface_point(traj_x,traj_y)[0])
                    count = count+1

                # 0.1 to cancel out the effect of downsampling
                average_vel = np.average((1/downsample)*np.linalg.norm(np.diff(np.array(points_3d),axis=0),axis=1))




            delta_T = average_vel / max_vel
            num_interp_pts = int(round(delta_T / panda_delta_T))

            print "Average Vel: ", average_vel
            print "Delta T:", delta_T
            print "# interp:", num_interp_pts

            # Don't allow zero
            if num_interp_pts < int(1):
                num_interp_pts = int(1)

            # Actually interpolate the forces
            starting_points, attractor_points, return_forces = dmps[xx].getForces()

            # First write mode to signal new DMP
            surface = segment[3]
            csvfile.write('mode'+','+surface+','+'')
            csvfile.write('\n')
            # Write selection vector
            # TODO: fix this with orientation
            csvfile.write(str(sel_vec[0])+','+str(sel_vec[1])+','+str(sel_vec[2]))
            csvfile.write('\n')
            csvfile.write(str(starting_points[0])+','+str(starting_points[1])+','+str(starting_points[2])+','+str(starting_points[3])+','+str(starting_points[4])+','+str(starting_points[5])+','+str(starting_points[6]))
            csvfile.write('\n')
            csvfile.write(str(attractor_points[0])+','+str(attractor_points[1])+','+str(attractor_points[2])+','+str(attractor_points[3])+','+str(attractor_points[4])+','+str(attractor_points[5])+','+str(attractor_points[6]))
            csvfile.write('\n')


            # TODO: This should be switched to SLERP for Orientation
            # Write all of the trajectory stuff
            for ii in range(0,len(return_forces[0])-1):
                # print trajectories[0][ii][0]
                for jj in range(0,num_interp_pts):
                    interp_x = return_forces[0][ii]+(float(jj)/float(num_interp_pts))*(return_forces[0][ii+1]-return_forces[0][ii])
                    interp_y = return_forces[1][ii]+(float(jj)/float(num_interp_pts))*(return_forces[1][ii+1]-return_forces[1][ii])
                    interp_z = return_forces[2][ii]+(float(jj)/float(num_interp_pts))*(return_forces[2][ii+1]-return_forces[2][ii])
                    interp_qx = return_forces[3][ii]+(float(jj)/float(num_interp_pts))*(return_forces[3][ii + 1] - return_forces[3][ii])
                    interp_qy = return_forces[4][ii]+(float(jj)/float(num_interp_pts))*(return_forces[4][ii + 1] - return_forces[4][ii])
                    interp_qz = return_forces[5][ii]+(float(jj)/float(num_interp_pts))*(return_forces[5][ii + 1] - return_forces[5][ii])
                    interp_qw = return_forces[6][ii]+(float(jj)/float(num_interp_pts))*(return_forces[6][ii + 1] - return_forces[6][ii])
                    csvfile.write(str(interp_x)+','+str(interp_y)+','+str(interp_z)+','+str(interp_qx)+','+str(interp_qy)+','+str(interp_qz)+','+str(interp_qw))
                    csvfile.write('\n')
            csvfile.write('variance' + ',' + '' + ',' + '')
            csvfile.write('\n')
            for ii in range(0,len(return_forces[0])-1):
                # print trajectories[0][ii][0]
                for jj in range(0,num_interp_pts):
                    csvfile.write(str(variances[0])+','+str(variances[1])+','+str(variances[2]))
                    csvfile.write('\n')

        # print np.shape(trajectories_plotting[2])
        # print demonstration_data_trimmed[0][:,2]
        # plot_paths_rviz(demonstration_data_trimmed,trajectories_plotting)


def main():
    global path0, path1, path2, path3, path4, pathDMP, forceDMP
    rospy.init_node('dmppathlistener', anonymous=True)
    pathDMP = rospy.Publisher('/dmp/pathdmp', Path, queue_size=1)
    forceDMP = rospy.Publisher('/dmp/forcedmp', MarkerArray, queue_size=1)
    path0 = rospy.Publisher('/dmp/path0', Path, queue_size=1)
    path1 = rospy.Publisher('/dmp/path1', Path, queue_size=1)
    path2 = rospy.Publisher('/dmp/path2', Path, queue_size=1)
    path3 = rospy.Publisher('/dmp/path3', Path, queue_size=1)
    path4 = rospy.Publisher('/dmp/path4', Path, queue_size=1)
    rospy.Subscriber("/dmp/filepub", String, loadData)
    rospy.Subscriber("/dmp/filepubsegmented", String, loadPresegmented)
    rospy.Subscriber("/dmp/reset", String, resetDMP)
    
    rospy.spin()

if __name__ == "__main__":
    main()




