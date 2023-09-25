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
import React from "react";

const FPS_UPDATE_INTERVAL = 1;

class VideoStreamControl extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            frame: null,
            fps: 0,
            ws: null,
            selected_camera: "front"
        };
        this.frame_counter = 0
        this.last_frame_ts = 0
        this.fps = 0
        this.slow_mode = false
    }

    start_streaming = (ws) => {
        console.log("Start streaming")
        ws.send("start")
    }

    componentDidMount() {
        this.connect();
    }
    timeout = 250; // Initial timeout duration as a class variable

    /**
     * @function connect
     * This function establishes the connect with the websocket and also ensures constant reconnection if connection closes
     */
    connect = () => {
        console.log("Connecting to video websocket");
        let ws_url = "ws://" + (window.location.port === "3000" ? "localhost:8080" : window.location.host) + "/ws/video_stream";

        var ws = new WebSocket(ws_url);
        let that = this; // cache the this
        var connectInterval;

        // websocket onopen event listener
        ws.onopen = () => {
            console.log("Connected to video websocket");

            this.start_streaming(ws);
            ws.onmessage = evt => {
                // listen to data sent from the websocket server
                this.new_frame(evt.data);
            }

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

    new_frame = async (frame) => {
        this.frame_counter += 1;
        var now = Date.now() / 1000;
        if (now - this.last_frame_ts > FPS_UPDATE_INTERVAL) {
            this.fps = Math.round(this.frame_counter / (now - this.last_frame_ts));
            this.frame_counter = 0;
            this.last_frame_ts = now;
        }
        this.setState({frame: await frame.arrayBuffer(), fps: this.fps});
        this.state.ws.send("ready");
    }

    handleMoveRobot = (e) => {
        let x_pos = e.x * 100;
        let y_pos = -e.y * 100;
        if (Math.abs(x_pos) < 2 && Math.abs(y_pos < 2)) {
            this.props.send_action("drive", "stop");
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

            this.props.send_action(
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
        this.props.send_action("drive", "stop");
    }

    set_camera_position = (e) => {
        this.props.send_action("camera", "set_position", {"position": e.target.value});
    }

    center_camera_position = (e) => {
        this.props.send_action("camera", "center_position");
    }

    render() {
        let base64String = "";
        if (this.state.frame !== null) {
            var binary = '';
            var bytes = new Uint8Array( this.state.frame );
            var len = bytes.byteLength;
            for (var i = 0; i < len; i++) {
                binary += String.fromCharCode( bytes[ i ] );
            }
            base64String = btoa(binary);
        }
        return (
            <Grid container direction="row" justifyContent="center" alignItems="center" style={{margin: 0, padding: 0}}>
                <Grid item xl={2} md={2} sm={2} xs={2} justifyContent="center" alignItems="center">
                    <Stack spacing={5} direction="column" alignItems="center" justifyContent="center">
                        <Joystick
                            size={window.outerWidth * 0.1}
                            stickSize={window.outerWidth * 0.05}
                            sticky={false}
                            baseColor="grey"
                            stickColor="black"
                            minDistance={2}
                            move={this.handleMoveRobot}
                            stop={this.handleStopRobot}>
                        </Joystick>
                        <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                            {this.props.config.robot_has_screen && (<IconButton onClick={this.props.send_action.bind(this, "camera", "capture_picture", {destination: "lcd"})}><CameraAltIcon/></IconButton>)}
                            <Tooltip title="Snapshot"><IconButton onClick={this.props.send_action.bind(this, "camera", "capture_picture", {})}><DownloadIcon/></IconButton></Tooltip>
                            {this.props.config.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera === "front" ? "arm" : "front", this.props.overlay, this.props.face_detection)}><SwitchCameraIcon/></IconButton>)}
                            {this.props.config.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera, !this.props.overlay, this.props.face_detection)}><PictureInPictureIcon/></IconButton>)}
                            <Tooltip title="Face Recognition"><IconButton onClick={this.props.send_action.bind(this, "face_detection", "toggle", {})}>{this.props.face_detection ? (<FaceRetouchingOffIcon/>):(<FaceIcon/>)}</IconButton></Tooltip>
                            <Tooltip title="Start Patrolling"><IconButton onClick={this.props.send_action.bind(this, "drive", "patrol", {})}><RadarIcon/></IconButton></Tooltip>
                            <Tooltip title="Stop Robot"><IconButton alt="Stop Robot" onClick={this.props.send_action.bind(this, "drive", "stop", {})}><DangerousIcon alt="Stop Robot"/></IconButton></Tooltip>
                        </Stack>
                    </Stack>
                </Grid>
                <Grid item xl={8} md={8} sm={8} xs={8} justifyContent="center" alignItems="center">
                    <img
                        src={`data:image/jpg;base64,${base64String}`}
                        style={{maxHeight: window.innerHeight * 0.8}}
                        width={window.outerWidth*0.7}
                        alt="Camera Feed"
                        onMouseMove={this.props.onMouseMove}
                        onClick={this.props.onClick}
                    />
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2} justifyContent="center" alignItems="center">
                    { this.props.config.robot_has_camera_servo && (<Stack
                        spacing={5}
                        justifyContent="center"
                        alignItems="center"
                        direction="column">
                        <Slider
                            min={0}
                            max={100}
                            step={1}
                            style={{height: window.innerHeight * 0.5}}
                            aria-label="Camera position"
                            orientation="vertical"
                            valueLabelDisplay="auto"
                            value={this.props.status.camera.position}
                            onChange={this.set_camera_position}
                            marks={[{value: this.props.status.camera.center_position}]}
                        />
                        <IconButton onClick={this.center_camera_position}><VerticalAlignCenterIcon/></IconButton>
                    </Stack>)}
                </Grid>
            </Grid>
        )
    }
}

export default VideoStreamControl;