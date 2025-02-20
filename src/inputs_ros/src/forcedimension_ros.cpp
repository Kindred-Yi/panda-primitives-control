#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <unistd.h>
#include <csignal>
#include <fstream>
#include <chrono>
#include <stdio.h>


// ROS
#include <ros/ros.h>
#include "geometry_msgs/Pose.h"
#include "geometry_msgs/Wrench.h"
#include "std_msgs/String.h"
#include "geometry_msgs/TransformStamped.h"
#include "geometry_msgs/Vector3.h"
#include "tf2_ros/transform_listener.h"


// Force Dimension
#include "dhdc.h"
#include <eigen3/Eigen/Geometry>

using namespace std::chrono;
using namespace std;

array<double,3> workspace_center = {0.42, 0., 0.19};
array<double,3> force_dimension = {0.0, 0.0, 0.0};
// Scaling Values
array<double,3> scaling_factors = {-5.0, -5.0, 5.0};
bool buttonPressed=false;
bool velocity_mode=false;
bool resetCenter=false;
bool idleMode = true;
double velcenterx = 0;
double velcentery = 0;
double velcenterz = 0;

std::ofstream outputfile;


void signalHandler(int sig)
{
    std::cout << "Interrupt " << sig << " recieved in ForceDimension.cpp\n";
    //cout << "Closing Force Dimension" << endl;
    //dhdClose();
    dhdEnableForce (DHD_OFF);
    exit(sig);
}

void fd_neutral_position(ros::Publisher fd_pos_pub){
    
    double x_d = 0.0;
    double y_d = 0.0;
    double z_d = 0.0;

    double x_curr, y_curr, z_curr;

    double v_x = 0.0;
    double v_y = 0.0;
    double v_z = 0.0;

    double stiffness = 200;
    double damping = 2*sqrt(stiffness);

    // Get current position and velocity
    dhdGetPosition (&x_curr, &y_curr, &z_curr);
    geometry_msgs::Vector3 fd_pos;
    fd_pos.x = x_curr;
    fd_pos.y = y_curr;
    fd_pos.z = z_curr;
    fd_pos_pub.publish(fd_pos);

    dhdGetLinearVelocity(&v_x,&v_y,&v_z);
    
    // Command to that position with P controller
    dhdSetForceAndTorque(-stiffness*(x_curr-x_d)-damping*v_x,-stiffness*(y_curr-y_d)-damping*v_y,
    -stiffness*(z_curr-z_d)-damping*v_z,0.0,0.0,0.0);

}

bool init_forcedimension() {
    cout <<"Setting up Force Dimension\n";
    if (dhdOpen () < 0) {
        cout << "Unable to open device" << endl;
        dhdSleep (2.0);
        return false;
    }
    cout << "Force Dimension Setup Complete" << endl;
    return true;
}

void poll_forcedimension(bool buttonPressed, double velcenterx, double velcentery,double velcenterz,ros::Publisher pose_goal_pub) {

    array<double, 6> panda_pos = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    
    double vx=0.0;
    double vy=0.0;
    double vz=0.0;
    double scaling = 0.001;

    if (buttonPressed){
        array<double, 3> force_dimension_temp = {0.0, 0.0, 0.0};
        dhdGetPosition (&force_dimension_temp[0], &force_dimension_temp[1], &force_dimension_temp[2]);
        panda_pos[0] = scaling_factors[0] * velcenterx + workspace_center[0];
        panda_pos[1] = scaling_factors[1] * velcentery + workspace_center[1];
        panda_pos[2] = scaling_factors[2] * velcenterz + workspace_center[2];

    }

    else{
        dhdGetPosition (&force_dimension[0], &force_dimension[1], &force_dimension[2]);
        if(resetCenter){
            cout << "Reset Center" << endl;
            workspace_center[0]=workspace_center[0]-scaling_factors[0]*(force_dimension[0]-velcenterx);
            workspace_center[1]=workspace_center[1]-scaling_factors[1]*(force_dimension[1]-velcentery);
            workspace_center[2]=workspace_center[2]-scaling_factors[2]*(force_dimension[2]-velcenterz);
        }
        
    }

    panda_pos[0] = scaling_factors[0] * force_dimension[0] + workspace_center[0];
    panda_pos[1] = scaling_factors[1] * force_dimension[1] + workspace_center[1];
    panda_pos[2] = scaling_factors[2] * force_dimension[2] + workspace_center[2];

    //cout << "FD: " << panda_pos[0]  << "," << panda_pos[1] << "," << panda_pos[2] << endl;
    //cout << "WC: " << workspace_center[0]  << "," << workspace_center[1] << "," << workspace_center[2] << endl;
    geometry_msgs::Pose pose;
    pose.position.x = panda_pos[0];
    pose.position.y = panda_pos[1];
    pose.position.z = panda_pos[2];
    pose.orientation.x = 0.0;
    pose.orientation.y = 0.0;
    pose.orientation.z = 0.0;
    pose.orientation.w = 1.0;
    pose_goal_pub.publish(pose);

}

void feedback_ft_forcedimension(geometry_msgs::Wrench wrench){

    double vx;
    double vy;
    double vz;
    double b = 50; // injected damping
    double scale = -0.4; //force scaling
    double vel_mode_stiffness = 5000;

    double fd_x;
    double fd_y;
    double fd_z;

    dhdGetLinearVelocity(&vx,&vy,&vz);
    dhdGetPosition (&fd_x, &fd_y, &fd_z);
    std::array<double, 6> FTData = {wrench.force.x, wrench.force.y, wrench.force.z, wrench.torque.x,
    wrench.torque.y, wrench.torque.z};
    
    Eigen::VectorXd v = Eigen::Map<Eigen::VectorXd>(FTData.data(),3);

    Eigen::Matrix3d m;
    m = Eigen::AngleAxisd(-M_PI/6, Eigen::Vector3d::UnitZ());
    v = m * v;

    FTData[0] = v[0];
    FTData[1] = v[1];
    FTData[2] = v[2];


    if(!velocity_mode && !idleMode){ 
        // If not clutching, render the forces on force dimension
        dhdSetForceAndTorque(FTData[0] * scale -vx*b,-FTData[1]* scale -vy*b,FTData[2]* scale -vz*b,0.0,0.0,0.0);
    }

    else{
        // Clutch should have zero foreces
        dhdSetForceAndTorque(0.0,0.0,0.0,0.0,0.0,0.0);
    }

    //cout << "FT: " << -FTData[0] * scale -vx*b  << "," << -FTData[1]* scale << "," << FTData[2]* scale -vz*b << endl;

}

void check_idle_mode(std_msgs::String event){
    if(event.data=="gui_takeover")
    {
        idleMode=true;
    }
}

int main(int argc, char **argv) {
    //Setup the signal handler for exiting
    signal(SIGINT, signalHandler);
    ros::init(argc, argv, "ForceDimension");
    ros::NodeHandle n("~");  

    if (!init_forcedimension()) {
        cout << endl << "Failed to init force dimension" << endl;
        return -1;
    }

    // Turn on gravity compensation
    dhdEnableForce (DHD_ON);

    // Second button press to start control & forces
    bool buttonReleased=false;
    while(!buttonReleased)
        if(dhdGetButton(0)==0) // button released
        {
            buttonReleased = true;
        }

    cout << "Press Button again to enable Forces and Panda Control" << endl;

    buttonPressed=false;
    while(!buttonPressed)
        if(dhdGetButton(0)==1) // button pressed
        {
            buttonPressed = true;
        }
    
    buttonReleased=false;
    while(!buttonReleased)
        if(dhdGetButton(0)==0) // button released
        {
            buttonReleased = true;
        }

    cout << "Control and Force Enabled" << endl;

    ros::Rate loop_rate(1000);

    ros::Publisher pose_goal_pub = 
        n.advertise<geometry_msgs::Pose>("/panda/cart_pose", 5);
    ros::Publisher command_pub = 
        n.advertise<std_msgs::String>("/panda/commands", 5);
    ros::Publisher event_pub = 
        n.advertise<std_msgs::String>("/event", 5);
    ros::Publisher fd_pos_pub = 
        n.advertise<geometry_msgs::Vector3>("/fd/position", 5);
    ros::Subscriber force_sub = n.subscribe("/panda/wrench", 5, feedback_ft_forcedimension);

    ros::Subscriber event_sub = n.subscribe("/event", 5, check_idle_mode);

    poll_forcedimension(false,0.0,0.0,0.0,pose_goal_pub);

    // Initialize data for storage
    double x = 0;
    double y = 0;
    double z = 0;
    double fx = 0;
    double fy = 0;
    double fz = 0;
    
    buttonPressed = false;
    velocity_mode = false;
    auto start = high_resolution_clock::now(); 
    bool gripping = false;
    tf2_ros::Buffer tfBuffer;
    tf2_ros::TransformListener tfListener(tfBuffer);

    while (ros::ok()) {
        // Get force dimension position and publish to ROS

        if(!idleMode){
            poll_forcedimension(velocity_mode, velcenterx,velcentery,velcenterz,pose_goal_pub);
        }

        else{
            fd_neutral_position(fd_pos_pub);
        }

        if (resetCenter){ //only allow one correction
            resetCenter=false;
        }

        // If button pressed and released in less than 0.3 seconds,
        // it is a gripping action

        // If held greater than 0.3 seconds, it is a clutch action

        if(!buttonPressed && dhdGetButton(0)==1) // button initially pressed
        {
            buttonPressed = true;
            start = high_resolution_clock::now(); 
        }

        
        if(buttonPressed) // button held
        {
            auto end = high_resolution_clock::now(); 
            auto duration = duration_cast<microseconds>(end - start); 

            if(duration.count()>=300000)
            {
                if (velocity_mode==false)
                {
                    velocity_mode=true;
                    // When starting a potential velocity mode action
                    // Need to see where the current center value is
                    dhdGetPosition (&velcenterx, &velcentery, &velcenterz);
                    cout << "Clutch Mode" << endl;
                }
               
            }
            
        }

        if(buttonPressed && dhdGetButton(0)==0) // button released
        {
            auto end = high_resolution_clock::now(); 
            auto duration = duration_cast<microseconds>(end - start); 

            if(duration.count()<300000)
            {
                // Single button press in idle mode is takeover
                if(idleMode){
                    idleMode=false;
                    std_msgs::String cmd;
                    cmd.data = "fd_takeover";
                    event_pub.publish(cmd);

                    geometry_msgs::TransformStamped transformStamped;
                    try{
                        //CHECK DURATION
                        transformStamped = tfBuffer.lookupTransform("panda_link0", "end_effector",ros::Time(0));
                    }
                    catch (tf2::TransformException &ex) {
                        ROS_WARN("%s",ex.what());
                    }
                    // TODO: THIS IS WHERE THE WORKSPACE CENTER IS!!!!
                    //workspace_center[0]=current_x-scaling_factors[0]*(force_dimension[0]-velcenterx);
                    //workspace_center[1]=current_y-scaling_factors[1]*(force_dimension[1]-velcentery);
                    //workspace_center[2]=current_z-scaling_factors[2]*(force_dimension[2]-velcenterz);
                    dhdGetPosition (&force_dimension[0], &force_dimension[1], &force_dimension[2]);

                    workspace_center[0]=transformStamped.transform.translation.x-scaling_factors[0]*(force_dimension[0]);
                    workspace_center[1]=transformStamped.transform.translation.y-scaling_factors[1]*(force_dimension[1]);
                    workspace_center[2]=transformStamped.transform.translation.z-scaling_factors[2]*(force_dimension[2]);
                }

                // Not in idle mode is gripper action
                else{
                    cout << "GRIPPER ACTION" << endl;
                    std_msgs::String cmd;
                    cmd.data = "toggleGrip";
                    command_pub.publish(cmd);
                }
            }

            buttonPressed=false;
        
            if (velocity_mode==true){
                // Deal with discontinuity
                resetCenter=true;
                velocity_mode=false;
            }
        }

        // Finish the loop
        ros::spinOnce();
        loop_rate.sleep(); 

    }

    dhdEnableForce (DHD_OFF);
    return 0;
}
