import React from 'react';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Grid from "@mui/material/Grid";
import Slider from "@mui/material/Slider";
import Stack from '@mui/material/Stack';
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import DangerousIcon from '@mui/icons-material/Dangerous';
import FaceIcon from '@mui/icons-material/Face';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import PhotoLibraryIcon from '@mui/icons-material/PhotoLibrary';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import StopIcon from '@mui/icons-material/Stop';
import IconButton from "@mui/material/IconButton";
import FaceRetouchingOffIcon from '@mui/icons-material/FaceRetouchingOff';
import Tooltip from "@mui/material/Tooltip";
import PictureInPictureIcon from '@mui/icons-material/PictureInPicture';
import SwitchCameraIcon from '@mui/icons-material/SwitchCamera';
import VerticalAlignCenterIcon from '@mui/icons-material/VerticalAlignCenter';
import RadarIcon from '@mui/icons-material/Radar';
import {Joystick} from "react-joystick-component";

import './App.css';
import VideoStreamControl from "./VideoStreamControl";


class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            ws: null,
            fps: 0,
            robot_config: {},
            robot_name: null,
            robot_status: {},
            selected_camera: "front",
            window_height: window.innerHeight,
            window_width: window.innerWidth,
            recording_video: false
        };
    }

    handleWindowResize = () => {
        this.setState({window_height: window.innerHeight, window_width: window.innerWidth});
    }

    componentDidMount() {
        this.connect();
        window.addEventListener('resize', this.handleWindowResize);
    }
    timeout = 250; // Initial timeout duration as a class variable

    /**
     * @function connect
     * This function establishes the connect with the websocket and also ensures constant reconnection if connection closes
     */
    connect = () => {
        console.log("Connecting to robot websocket");
        let ws_url = "ws://" + (window.location.port === "3000" ? "localhost:8080" : window.location.host) + "/ws/robot";

        var ws = new WebSocket(ws_url);
        let that = this; // cache the this
        var connectInterval;

        // websocket onopen event listener
        ws.onopen = () => {
            console.log("Connected to robot websocket");

            this.setState({ ws: ws });

            that.timeout = 250; // reset timer to 250 on open of websocket connection
            clearTimeout(connectInterval); // clear Interval on on open of websocket connection
        };

        // websocket onclose event listener
        ws.onclose = e => {
            console.log(
                `Socket is closed. Reconnect will be attempted in ${Math.min(
                    10000 / 1000,
                    (that.timeout + that.timeout) / 1000
                )} second.`,
                e.reason
            );

            that.timeout = that.timeout + that.timeout; //increment retry interval
            connectInterval = setTimeout(this.check, Math.min(10000, that.timeout)); //call check function after timeout
        };

        ws.onmessage = evt => {
            // listen to data sent from the websocket server
            var message = JSON.parse(evt.data);
            if (message.topic === "status") {
                this.updateStatus(message.message)
            } else if (message.topic === "video") {
                console.log(message)
                this.setState({recording_video: message.message.status === "recording"})
            } else {
                console.log("Unknown message topic " + message.topic)
            }
        }

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );

            ws.close();
        };
    };

    /**
     * utilited by the @function connect to check if the connection is close, if so attempts to reconnect
     */
    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState === WebSocket.CLOSED) this.connect(); //check if websocket instance is closed, if so call `connect` function.
    };

    updateStatus = (status) => {
        this.setState({robot_config: status.config, robot_name: status.robot_name, robot_status: status.status});
    }

    send_action = (type, action, args={}) => {
        this.send_json({topic: "robot", message: {type: type, action: action, args: args}});
    }

    send_json = (json_data) => {
        this.state.ws.send(
            JSON.stringify(json_data)
        );
    }

    handleMoveRobot = (e) => {
        let x_pos = e.x * 100;
        let y_pos = -e.y * 100;
        if (Math.abs(x_pos) < 2 && Math.abs(y_pos < 2)) {
            this.send_action("drive", "stop");
        }
        else {

            let right_speed = Math.min(Math.max(-y_pos - x_pos, -100), 100)
            let left_speed = Math.min(Math.max(-y_pos + x_pos, -100), 100)

            if (this.motor_slow_mode) {
                right_speed = Math.round(0.3 * right_speed)
                left_speed = Math.round(0.3 * left_speed)
            }

            let left_orientation = 'F';
            if (left_speed < 0)
                left_orientation = 'B'


            let right_orientation = 'F'
            if (right_speed < 0)
                right_orientation = 'B'

            this.send_action(
                "drive",
                "move",
                {
                    left_orientation: left_orientation,
                    left_speed: Math.abs(left_speed),
                    right_orientation: right_orientation,
                    right_speed: Math.abs(right_speed),
                    duration: 30,
                    distance: null,
                    rotation: null,
                    auto_stop: false,
                }
             );
        }
    }

    handleStopRobot = (e) => {
        this.send_action("drive", "stop");
    }

    set_camera_position = (e) => {
        this.send_action("camera", "set_position", {"position": e.target.value});
    }

    center_camera_position = (e) => {
        this.send_action("camera", "center_position");
    }

    updateFps = (fps) => {
        this.setState({fps: fps})
    }

    render() {
        document.body.style.overflow = "hidden";
        if (document.body.fullscreenEnabled) {
            document.body.requestFullscreen();
        }
        return (
            <div className="App" style={{display: this.state.window_height > 400 ? "flex" : "block"}}>
                <Grid container direction="column" alignItems="center" justifyContent="space-evently">
                    <Grid item xs={2}>
                        <Box sx={{display: 'flex', width: 'fit-content', bgcolor: 'grey', border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1}}>
                            {this.state.robot_config.robot_has_back_camera && (<Divider orientation="vertical" flexItem/>)}
                            {this.state.robot_config.robot_has_back_camera && (<IconButton onClick={this.stream_setup_callback.bind(this, this.selected_camera === "front" ? "arm" : "front", this.overlay, this.face_detection)}><SwitchCameraIcon/></IconButton>)}
                            {this.state.robot_config.robot_has_back_camera && (<IconButton onClick={this.stream_setup_callback.bind(this, this.selected_camera, !this.overlay, this.face_detection)}><PictureInPictureIcon/></IconButton>)}
                            {!this.state.recording_video && (<Tooltip title="Record a Video"><IconButton onClick={this.send_action.bind(this, "camera", "start_video", {})}><FiberManualRecordIcon/></IconButton></Tooltip>)}
                            {this.state.recording_video && (<Tooltip title="Stop Video Recording"><IconButton onClick={this.send_action.bind(this, "camera", "stop_video", {})}><StopIcon/></IconButton></Tooltip>)}
                            <Tooltip title="Take a Photo"><IconButton onClick={this.send_action.bind(this, "camera", "capture_picture", {})}><CameraAltIcon/></IconButton></Tooltip>
                            <Divider orientation="vertical" flexItem/>
                            <Tooltip title="Open photo library"><IconButton onClick={window.open.bind(window, '/pictures', '_blank')}><PhotoLibraryIcon/></IconButton></Tooltip>
                            <Tooltip title="Open video library"><IconButton onClick={window.open.bind(window, '/videos', '_blank')}><VideoLibraryIcon/></IconButton></Tooltip>
                            <Divider orientation="vertical" flexItem/>
                            <Tooltip title="Face Recognition"><IconButton onClick={this.send_action.bind(this, "face_detection", "toggle", {})}>{this.face_detection ? (<FaceRetouchingOffIcon/>):(<FaceIcon/>)}</IconButton></Tooltip>
                            <Tooltip title="Start Patrolling"><IconButton onClick={this.send_action.bind(this, "drive", "patrol", {})}><RadarIcon/></IconButton></Tooltip>
                            <Tooltip title="Stop Robot"><IconButton alt="Stop Robot" onClick={this.send_action.bind(this, "drive", "stop", {})}><DangerousIcon alt="Stop Robot"/></IconButton></Tooltip>
                        </Box>
                    </Grid>
                    <Grid container item xs={10} style={{margin: 0, padding: 0}}>
                        <Grid container item direction="row" justifyContent="center" alignItems="center" style={{margin: 0, padding: 0}}>
                            <Grid container item xs={2} justifyContent="center" alignItems="center">
                                <Joystick
                                    size={this.state.window_width * 1.5 / 12.0}
                                    stickSize={this.state.window_width * 0.7 / 12.0}
                                    sticky={false}
                                    baseColor="grey"
                                    stickColor="black"
                                    minDistance={2}
                                    move={this.handleMoveRobot}
                                    stop={this.handleStopRobot}>
                                </Joystick>
                            </Grid>
                            <Grid container item xs={8} justifyContent="center" alignItems="center">
                                <VideoStreamControl
                                    max_height={this.state.window_height * 9.0 / 12.0}
                                    max_width={this.state.window_width * 8.0 / 12.0}
                                    onMouseMove={this.onMouseMove}
                                    onClick={this.onClick}
                                    updateFps={this.updateFps}
                                />
                            </Grid>
                            <Grid container item xs={2} justifyContent="center" alignItems="center">
                                { this.state.robot_config.robot_has_camera_servo && (<Stack
                                    spacing={2}
                                    justifyContent="center"
                                    alignItems="center"
                                    direction="column">
                                    <Slider
                                        min={0}
                                        max={100}
                                        step={1}
                                        style={{height: this.state.window_height * 0.4}}
                                        aria-label="Camera position"
                                        orientation="vertical"
                                        valueLabelDisplay="auto"
                                        value={this.state.robot_status.camera.position}
                                        onChange={this.set_camera_position}
                                        marks={[{value: this.state.robot_status.camera.center_position}]}
                                    />
                                    <IconButton onClick={this.center_camera_position}><VerticalAlignCenterIcon/></IconButton>
                                </Stack>)}
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={2} alignItems="top">
                        <p style={{margin: 0, padding: 0, fontSize: "20px"}}>Connected to {this.state.robot_name} - {this.state.fps} FPS</p>
                    </Grid>
                </Grid>
            </div>
        );
    }
}

export default App;
