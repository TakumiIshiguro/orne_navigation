#!/usr/bin/env python3

"""Save the final occupancy grid after the rosbag player exits."""

import os
import subprocess
import time

import rosnode
import rospy
from nav_msgs.msg import OccupancyGrid


class FinalMapSaver:
    def __init__(self):
        self.bag_node = rospy.get_param("~bag_node", "/bag_player")
        self.map_topic = rospy.get_param("~map_topic", "/map")
        self.map_file = os.path.abspath(
            os.path.expanduser(rospy.get_param("~map_file", "/tmp/bag_map"))
        )
        self.received_map = False
        rospy.Subscriber(self.map_topic, OccupancyGrid, self._map_callback, queue_size=1)

    def _map_callback(self, _message):
        self.received_map = True

    def run(self):
        bag_started = False
        rospy.loginfo("Waiting for rosbag player %s", self.bag_node)

        # Use wall time: simulated ROS time stops when bag playback finishes.
        while not rospy.is_shutdown():
            try:
                bag_running = self.bag_node in rosnode.get_node_names()
            except rosnode.ROSNodeIOException:
                bag_running = False

            if bag_running:
                bag_started = True
            elif bag_started:
                break
            time.sleep(0.1)

        if rospy.is_shutdown():
            return

        # Allow the final scan callback and map update to complete.
        time.sleep(2.5)
        if not self.received_map:
            rospy.logerr("Bag finished but no map was received on %s", self.map_topic)
            rospy.signal_shutdown("no map received")
            return

        output_dir = os.path.dirname(self.map_file)
        os.makedirs(output_dir, exist_ok=True)
        command = [
            "rosrun",
            "map_server",
            "map_saver",
            "-f",
            self.map_file,
            "map:=" + self.map_topic,
        ]
        rospy.loginfo("Saving final map to %s.[pgm|yaml]", self.map_file)
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            rospy.logerr("map_saver failed with exit code %s", error.returncode)
            rospy.signal_shutdown("map_saver failed")
            return

        # Keep the YAML portable when the map directory is moved or shared.
        yaml_file = self.map_file + ".yaml"
        with open(yaml_file, "r", encoding="utf-8") as stream:
            yaml_lines = stream.readlines()
        with open(yaml_file, "w", encoding="utf-8") as stream:
            for line in yaml_lines:
                if line.startswith("image:"):
                    line = "image: " + os.path.basename(self.map_file) + ".pgm\n"
                stream.write(line)

        rospy.loginfo("Final map saved successfully")
        rospy.signal_shutdown("map saved")


if __name__ == "__main__":
    rospy.init_node("save_map_after_bag")
    FinalMapSaver().run()
