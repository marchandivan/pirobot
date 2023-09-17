import Grid from "@mui/material/Grid";
import Slider from "@mui/material/Slider";
import Stack from '@mui/material/Stack';
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import DangerousIcon from '@mui/icons-material/Dangerous';
import DownloadIcon from '@mui/icons-material/Download';
import FaceIcon from '@mui/icons-material/Face';
import IconButton from "@mui/material/IconButton";
import FaceRetouchingOffIcon from '@mui/icons-material/FaceRetouchingOff';
import Tooltip from "@mui/material/Tooltip";
import PictureInPictureIcon from '@mui/icons-material/PictureInPicture';
import SwitchCameraIcon from '@mui/icons-material/SwitchCamera';
import VerticalAlignCenterIcon from '@mui/icons-material/VerticalAlignCenter';
import RadarIcon from '@mui/icons-material/Radar';
import {Joystick} from "react-joystick-component";
import {View} from "react-native";
import React from "react";

const FPS_UPDATE_INTERVAL = 1;

class VideoStreamControl extends React.Component {

    constructor(props) {
        super(props);
        this.socket = props.socket;
        this.state = {
            frame: null,
            fps: 0
        };
        this.frame_counter = 0
        this.last_frame_ts = 0
        this.fps = 0
    }

    start_streaming = () => {
        this.socket.emit("video_stream", "start");
    }

    componentDidMount() {
        this.socket.on("video_frame", this.new_frame);
        this.socket.on("connect", this.start_streaming)
        this.start_streaming();
    }

    new_frame = (frame) => {
        this.frame_counter += 1;
        var now = Date.now() / 1000;
        if (now - this.last_frame_ts > FPS_UPDATE_INTERVAL) {
            this.fps = Math.round(this.frame_counter / (now - this.last_frame_ts));
            this.frame_counter = 0;
            this.last_frame_ts = now;
        }
        this.setState({frame: frame, fps: this.fps});
        this.socket.emit("video_stream", "ready");
    }

    handleMoveRobot = (e) => {
        console.log(e);
    }

    handleStopRobot = (e) => {
        console.log(e);
    }

    render() {
        const base64String = btoa(String.fromCharCode(...new Uint8Array(this.state.frame)));
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <img
                        src={`data:image/jpeg;base64,${base64String}`}
                        //style={{maxHeight: window.outerHeight * 0.7}}
                        width={window.outerWidth}
                        height={window.outerHeight*.7}
                        alt="Camera Feed"
                        onMouseMove={this.props.onMouseMove}
                        onClick={this.props.onClick}
                    />
                    <View style={{position: 'absolute', top: -window.outerHeight * 0.6, left: window.outerWidth * 0.6, width: 300, height: 300, justifyContent: 'center', alignItems: 'center'}}>
                        <Joystick
                            size={200}
                            stickSize={100}
                            sticky={false}
                            baseColor="grey"
                            stickColor="#00FF00"
                            move={this.handleMoveRobot}
                            stop={this.handleStopRobot}>
                        </Joystick>
                    </View>
                    <View style={{position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center'}}>
                        <Stack
                            sx={{ height: 500 }}
                            justifyContent="center"
                            alignItems="center"
                            direction="column">
                            <Slider
                                min={0}
                                max={100}
                                step={1}
                                aria-label="Camera position"
                                orientation="vertical"
                                valueLabelDisplay="auto"
                                value={this.props.camera_position}
                                onChange={this.props.set_camera_position}
                                marks={[{value: this.props.center_position}]}
                            />
                            <IconButton onClick={this.props.centerCameraPosition}><VerticalAlignCenterIcon/></IconButton>
                        </Stack>
                    </View>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                  <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                    {this.props.robot_has_screen && (<IconButton onClick={this.props.capture_image_callback.bind(this, "lcd", this.props.selected_camera)}><CameraAltIcon/></IconButton>)}
                    <Tooltip title="Snapshot"><IconButton onClick={this.props.send_action.bind(this, "camera", "capture_picture", {})}><DownloadIcon/></IconButton></Tooltip>
                    {this.props.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera === "front" ? "arm" : "front", this.props.overlay, this.props.face_detection)}><SwitchCameraIcon/></IconButton>)}
                    {this.props.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera, !this.props.overlay, this.props.face_detection)}><PictureInPictureIcon/></IconButton>)}
                    <Tooltip title="Face Recognition"><IconButton onClick={this.props.send_action.bind(this, "face_detection", "toggle", {})}>{this.props.face_detection ? (<FaceRetouchingOffIcon/>):(<FaceIcon/>)}</IconButton></Tooltip>
                    <Tooltip title="Start Patrolling"><IconButton onClick={this.props.send_action.bind(this, "drive", "patrol", {})}><RadarIcon/></IconButton></Tooltip>
                    <Tooltip title="Stop Robot"><IconButton alt="Stop Robot" onClick={this.props.send_action.bind(this, "drive", "stop", {})}><DangerousIcon alt="Stop Robot"/></IconButton></Tooltip>
                    <p>FPS: {this.state.fps}</p>
                  </Stack>
                </Grid>
            </Grid>
        )
    }
}

export default VideoStreamControl;