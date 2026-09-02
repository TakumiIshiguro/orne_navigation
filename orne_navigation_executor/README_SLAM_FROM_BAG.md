# rosbagからの地図作成

`/scan`、`/tf`、`/tf_static`、`/odom`をbagから再生し、GMappingで
OccupancyGridを作成します。画像トピックは再生しないため、大きなbagでも
不要な画像デコードは発生しません。

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch orne_navigation_executor slam_from_bag.launch \
  bag_file:=/absolute/path/to/input.bag \
  map_file:=/absolute/path/to/output/map_name
```

bagの再生終了後、`map_name.pgm`と`map_name.yaml`が自動的に保存されます。
保存先ディレクトリが存在しない場合は自動作成されます。

高速に処理する場合は`rate`を指定します。

```bash
roslaunch orne_navigation_executor slam_from_bag.launch \
  bag_file:=/absolute/path/to/input.bag \
  map_file:=/absolute/path/to/output/map_name \
  rate:=2.0 rviz:=false
```

別名のトピックやフレームを収録したbagでは、`scan_topic`、`odom_topic`、
`base_frame`、`odom_frame`を上書きしてください。
