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

## How to run

You need **4 terminals**. Run the steps in order and keep each terminal open.

### 0. Build the package (first time, or after code changes)

```bash
cd ~/ros2_ws
colcon build --packages-select corridor_navigation
source install/setup.bash
```

### 1. Terminal 1: start Gazebo with the corridor world

```bash
export GZ_SIM_RESOURCE_PATH=$HOME/ardupilot_gazebo/models:$HOME/ardupilot_gazebo/worlds:$GZ_SIM_RESOURCE_PATH
export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/ardupilot_gazebo/build:$GZ_SIM_SYSTEM_PLUGIN_PATH
source ~/ros2_ws/install/setup.bash
ros2 launch corridor_navigation launch.py
```

Wait until Gazebo opens and the Iris drone appears in the corridor.

### 2. Terminal 2: start ArduPilot SITL

```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --out 127.0.0.1:14551
```

The `--out 127.0.0.1:14551` part forwards MAVLink so MAVROS can connect to the simulated drone.

### 3. Terminal 3: check that MAVROS is connected

```bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /mavros/state --once
```

You should see `connected: true`. If it says `false`, wait a few seconds and run it again. Do not continue until it is connected.

### 4. Take off (in the SITL / MAVProxy console from Terminal 2)

```
mode guided
arm throttle
takeoff 2
```

Wait for the drone to reach about 2 m.

### 5. Terminal 4: run the centering node

```bash
source ~/ros2_ws/install/setup.bash
ros2 run corridor_navigation centering_node
```

The drone should now fly down the corridor, stay centered between the walls, and stop near the end wall.
