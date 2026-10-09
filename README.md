# corridor_navigation

A ROS 2 package that makes an Iris quadcopter fly down a corridor on its own and stay in the middle, using only its onboard lidar. It runs in Gazebo Harmonic with ArduPilot SITL and ROS 2 Jazzy.

## Idea

The drone scans the walls on its left and right and compares the two distances:

- more room on the left than on the right: move left
- more room on the right: move right
- equal: keep going straight

The sideways speed is proportional to the difference, so the drone settles in the middle of the corridor. It keeps a slow, constant forward speed and stops when the wall ahead gets close (the far end of the corridor).

Because it only compares the left and right readings, it never needs the corridor's coordinates or width, so the same code works in corridors of different widths.

## How it is built

- `centering_node`: reads the lidar scan, works out the left/right difference and sends velocity commands to the drone through MAVROS.
- `corridor_world.sdf`: the test corridor (two side walls and an end wall).
- The Iris model has a 2D lidar attached, bridged into ROS 2 as `/lidar`.
