import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import TextField from "@material-ui/core/TextField";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import React from 'react';
import './App.css';
import Cookies from 'js-cookie';
import ArmControl from "./ArmContorl"
import DirectionCross from "./DirectionCross";
import LightControl from "./LightControl"
import ScreenControl from "./ScreenControl"
import VideoStreamControl from "./VideoStreamControl";
import Divider from '@material-ui/core/Divider';

const KEY_UP = 38
const KEY_DOWN = 40
const KEY_LEFT = 37
const KEY_RIGHT = 39
const KEY_ESC = 27
const KEY_SPACE = 32
const KEY_0 = 48
const KEY_9 = 57

const MOVE_KEYS = [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]

const MOVE_INTENT_FORWARD = 0
const MOVE_INTENT_FORWARD_RIGHT = 1
const MOVE_INTENT_FORWARD_LEFT = 2
const MOVE_INTENT_FORWARD_SLIGHT_RIGHT = 3
const MOVE_INTENT_FORWARD_SLIGHT_LEFT = 4
const MOVE_INTENT_BACKWARD = 5
const MOVE_INTENT_BACKWARD_RIGHT = 6
const MOVE_INTENT_BACKWARD_LEFT = 7
const MOVE_INTENT_BACKWARD_SLIGHT_RIGHT = 8
const MOVE_INTENT_BACKWARD_SLIGHT_LEFT = 9
const MOVE_INTENT_U_TURN_RIGHT = 10
const MOVE_INTENT_U_TURN_LEFT = 11
const MOVE_INTENT_STOP = 11
const MOVE_INTENT_SLIGHT_LEFT = 12
const MOVE_INTENT_SLIGHT_RIGHT = 13

class App extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            left_on: false,
            right_on: false,
            arm_on: false,
            speed: 50,
            min_duration: 0.2,
            max_duration: 20.0,
            mouse_x: 0,
            mouse_y: 0,
            selected_camera: "front",
            stream_overlay: true,
            face_detection: false,
            lcd_brightness: 100,
            mood: "relaxed",
            moods: ["relaxed"],
            arm_position_claw: 0,
            arm_position_wrist: 0,
            lock_wrist: true,
            arm_position_forearm: 0,
            arm_position_shoulder: 0,
            distance: 10,
            rotation: 10,
            speech_destination: "audio",
            camera_position: 0,
            center_position: 50
        }
        this.key_down = {};
        this.config = {};
    }

    componentDidMount() {
        let url = '/api/status/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url)
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
        // Register keydown event
        document.addEventListener("keydown", this.keyDown, false);
        document.addEventListener("keyup", this.keyUp, false);
    }

    componentWillUnmount(){
        document.removeEventListener("keydown", this.keyDown, false);
        document.removeEventListener("keyup", this.keyUp, false);
      }

    keyDown = (event) => {
        this.key_down[event.keyCode] = true;
        if (event.keyCode === KEY_ESC || event.keyCode === KEY_SPACE) {
            this.stopRobot()
        } else if (MOVE_KEYS.includes(event.keyCode)) {
            this.moveKeyDown();
        } else if ( KEY_0 <= event.keyCode && event.keyCode <= KEY_9) {
            if (event.keyCode === KEY_0) {
                this.setState({
                    speed: 100
                })
            } else {
                this.setState({
                    speed: (event.keyCode - KEY_0) * 10
                })
            }
        }

    }

    keyUp = (event) => {
        this.key_down[event.keyCode] = false;
    }

    moveKeyDown = () => {
        let move_intent = MOVE_INTENT_STOP;
        if (this.key_down[KEY_UP]) {
            if (this.key_down[KEY_LEFT]) {
                move_intent = MOVE_INTENT_FORWARD_LEFT;
            } else if (this.key_down[KEY_RIGHT]) {
                move_intent = MOVE_INTENT_FORWARD_RIGHT;
            } else {
                move_intent = MOVE_INTENT_FORWARD
            }
        } else if (this.key_down[KEY_DOWN]) {
            if (this.key_down[KEY_LEFT]) {
                move_intent = MOVE_INTENT_BACKWARD_LEFT;
            } else if (this.key_down[KEY_RIGHT]) {
                move_intent = MOVE_INTENT_BACKWARD_RIGHT;
            } else {
                move_intent = MOVE_INTENT_BACKWARD
            }
        } else if (this.key_down[KEY_LEFT]) {
            move_intent = MOVE_INTENT_SLIGHT_LEFT;
        } else if (this.key_down[KEY_RIGHT]) {
            move_intent = MOVE_INTENT_SLIGHT_RIGHT;
        }

        this.moveRobot(move_intent);
    }

    updateState = (data) => {
        if (data.status === "OK") {
            this.setState({
                left_on: data.robot.light.left_on,
                right_on: data.robot.light.right_on,
                arm_on: data.robot.light.arm_on,
                moods: data.robot.moods,
                streaming: data.robot.camera.streaming,
                selected_camera: data.robot.camera.selected_camera,
                stream_overlay: data.robot.camera.overlay,
                face_detection: data.robot.camera.face_detection,
                camera_position: data.robot.camera.position,
                center_position: data.robot.camera.center_position,
                arm_position_claw: data.robot.arm.position.claw,
                arm_max_angle_claw: data.robot.arm.config.claw.max_angle,
                arm_position_wrist: data.robot.arm.position.wrist,
                arm_max_angle_wrist: data.robot.arm.config.wrist.max_angle,
                arm_position_forearm: data.robot.arm.position.forearm,
                arm_max_angle_forearm: data.robot.arm.config.forearm.max_angle,
                arm_position_shoulder: data.robot.arm.position.shoulder,
                arm_max_angle_shoulder: data.robot.arm.config.shoulder.max_angle
            });
            if ('config' in data) {
                this.config = data.config;
            }
        } else {
            console.error(data.message);
        }
    }

    updateSpeed = (event, value) => {
        this.setState({
            speed: value
        })
    }

    updateDistance = (event, value) => {
        this.setState({
            distance: value
        })
    }

    getDistanceTimeout = () => {
        return Math.max(Math.min(this.getDistanceValue() * 4 * (this.state.max_duration / 1.8) * (100 / this.state.speed), this.state.max_duration), this.state.min_duration);
    }

    updateRotation = (event, value) => {
        this.setState({
            rotation: value
        })
    }

    getRotationTimeout = (rotation=null) => {
        if (rotation == null) {
            rotation = this.state.rotation;
        }
        return Math.max(Math.min(rotation * (10 / 180.0) * (100 / this.state.speed), this.state.max_duration), this.state.min_duration);
    }

    keyPress = (e) => {
        if(e.keyCode === 13 && e.target.value !== ""){
            this.saySomething( e.target.value)
            e.target.value = "";
        }
    }

    onMouseMove = (e) => {
        let client_rect = e.target.getBoundingClientRect()
        this.setState({ mouse_x: 100 * (e.clientX - client_rect.x + 1) / client_rect.width,
                              mouse_y: 100 * (e.clientY - client_rect.y + 1) / client_rect.height });
    }

    onStreamClick = (e) => {
        // Double click
        if (e.detail === 2) {
            this.moveToTarget();
        }
    }

    setCameraPosition = (event, value) => {
        let url = '/api/set_camera_position/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                position: value
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    centerCameraPosition = () => {
        let url = '/api/center_camera_position/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    moveToTarget = (e) => {
        let url = '/api/move_to_target/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                x: this.state.mouse_x,
                y: this.state.mouse_y,
                speed: this.state.speed,
                timeout: this.state.max_duration
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    saySomething = (text) => {
        let url = '/api/say/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                destination: this.state.speech_destination,
                text: text
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    moveRobot = (move_intent) => {
        let left_orientation = 'F';
        let left_speed = 0.0;
        let right_orientation = 'F';
        let right_speed = 0.0;
        let distance = null;
        let rotation = null;
        let duration = this.state.max_duration;
        switch (move_intent) {
            case MOVE_INTENT_FORWARD:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 1.0;
                distance = this.getDistanceValue();
                break;
            case MOVE_INTENT_FORWARD_SLIGHT_LEFT:
                left_orientation = 'F';
                left_speed = 0.5;
                right_orientation ='F'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_FORWARD_LEFT:
                left_orientation = 'F';
                left_speed = 0.0;
                right_orientation ='F'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_FORWARD_SLIGHT_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.5;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_FORWARD_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_U_TURN_LEFT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 1.0;
                rotation = 180;
                break;
            case MOVE_INTENT_U_TURN_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                rotation = 180;
                break;
            case MOVE_INTENT_SLIGHT_LEFT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_SLIGHT_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_BACKWARD:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                distance = this.getDistanceValue();
                break;
            case MOVE_INTENT_BACKWARD_SLIGHT_LEFT:
                left_orientation = 'B';
                left_speed = 0.5;
                right_orientation ='B'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_BACKWARD_LEFT:
                left_orientation = 'B';
                left_speed = 0.0;
                right_orientation ='B'
                right_speed = 1.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_BACKWARD_SLIGHT_RIGHT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.5;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_BACKWARD_RIGHT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.0;
                rotation = this.state.rotation;
                break;
            case MOVE_INTENT_STOP:
            default:
                left_orientation = 'F';
                left_speed = 0.0;
                right_orientation ='F'
                right_speed = 0.0;
                break;
        }

        if (distance != null) {
            duration = this.getDistanceTimeout();
        } else if (rotation != null) {
            duration = this.getRotationTimeout(rotation);
        }

        let url = '/api/move/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                left_orientation: left_orientation,
                left_speed: left_speed * this.state.speed,
                right_orientation: right_orientation,
                right_speed: right_speed * this.state.speed,
                duration: duration,
                distance: distance,
                rotation: rotation
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    stopRobot = () => {
        let url = '/api/stop/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({})
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    setLight = (left_on, right_on, arm_on) => {
        let url = '/api/set_light/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                left_on: left_on,
                right_on: right_on,
                arm_on: arm_on
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    setupStream = (selected_camera, overlay, face_detection) => {
        let url = '/api/stream_setup/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                selected_camera: selected_camera,
                overlay: overlay,
                face_detection: face_detection
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    updateMood = (event) => {
        this.setState({
            mood: event.target.value
        })
        this.setMood(event.target.value);
    }

    setMood = (mood) => {
        let url = '/api/mood/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                mood: mood,
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    setLcdPicture = (name) => {
        let url = '/api/lcd_picture/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                name: name,
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

     captureImage = async (destination, camera) => {
        let url = '/api/capture_image/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                destination: destination,
                camera: camera
            })
        })
        .catch((error) => {
            console.error('Error:', error);
            return;
        });
        if (response.headers.get("content-type") === "image/png") {
            const filename = response.headers.get('filename');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            // the filename you want
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            alert("your file has downloaded!"); // or you know, something with better UX...
        } else {
            this.updateState(response.json());
        }
    }

    updateLcdBrightness = (value) => {
        this.setState({
            lcd_brightness: value
        })
        let url = '/api/set_lcd_brightness/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                brightness: value
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    resetLcdScreen = () => {
        let url = '/api/reset_lcd/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            }
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    moveArm = (id, value) => {
        let url = '/api/move_arm/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                id: id,
                angle: value,
                lock_wrist: this.state.lock_wrist
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    moveArmToPosition = (position_id) => {
        console.log(position_id)
        let url = '/api/move_arm_to_position/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                position_id: position_id,
                lock_wrist: this.state.lock_wrist
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    patrol = (speed) => {
        let url = '/api/patrol/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                speed: speed
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    setWristLock = (locked) => {
        this.setState({
            lock_wrist: !this.state.lock_wrist
        })
    }

    calculateDistanceValue = (value) => {
        if (value < 10) {
            return value / 1000;
        }
        else if (value < 20) {
            return (1 + value - 10) / 100;
        } else {
            return (1 + value - 20) / 10;
        }
    }

    getDistanceValue = () => {
        return this.calculateDistanceValue(this.state.distance);
    }

    distanceLabelFormat = (value) => {
        let distance = this.getDistanceValue();
        if (distance < 0.01) {
            return `${parseInt(distance * 1000)}mm`;
        } else if (distance < 1) {
            return `${parseInt(distance * 100)}cm`;
        } else {
            return `${parseInt(distance)}m`;
        }
    }

    toggleSpeechDestination = (event) => {
        if (event.target.checked) {
            this.setState({speech_destination: this.state.speech_destination === "lcd" ? "audio" : "lcd"})
        }
    }

    render() {
        return (
            <div className="App" >
                <header className="App-header">
                    <Grid container spacing={0} direction="row" justifyContent="center" alignItems="center">
                        <Grid item xl={2} md={2} sm={2} xs={12}>
                            <Grid item xl={12} md={12} sm={12} xs={12}>
                                <LightControl
                                    hide={!this.config.robot_has_light}
                                    set_light_callback={this.setLight}
                                    left_on={this.state.left_on}
                                    right_on={this.state.right_on}
                                    arm_on={this.state.arm_on}
                                />
                            </Grid>
                            <ScreenControl
                             hide={!this.config.robot_has_screen}
                             updateLcdBrightness={this.updateLcdBrightness}
                             resetLcdScreen={this.resetLcdScreen}
                             setLcdPicture={this.setLcdPicture}
                             mood={this.state.mood}
                             moods={this.state.moods}
                             updateMood={this.updateMood}
                             />
                            <Grid container>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Say Something
                                    </p>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={10} md={10} sm={10} xs={10}>
                                    <TextField onKeyDown={this.keyPress} fullWidth={true}/>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <p/>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={10} md={10} sm={10} xs={10}>
                                <FormGroup row={true}>
                                  <FormControlLabel control={<Checkbox onChange={this.toggleSpeechDestination} checked={this.state.speech_destination === "lcd"}/>} label="Display" />
                                  <FormControlLabel control={<Checkbox onChange={this.toggleSpeechDestination} checked={this.state.speech_destination === "audio"}/>} label="Speak" />
                                </FormGroup>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                            </Grid>
                        </Grid>
                        <Grid item xl={8} md={8} sm={8} xs={12}>
                            <VideoStreamControl
                                onMouseMove={this.onMouseMove}
                                onClick={this.onStreamClick}
                                capture_image_callback={this.captureImage}
                                stream_setup_callback={this.setupStream}
                                selected_camera={this.state.selected_camera}
                                overlay={this.state.stream_overlay}
                                face_detection={this.state.face_detection}
                                patrol={this.patrol.bind(this, this.state.speed)}
                                stopRobot={this.stopRobot}
                                robot_has_back_camera={this.config.robot_has_back_camera}
                                robot_has_screen={this.config.robot_has_screen}
                                set_camera_position={this.setCameraPosition}
                                centerCameraPosition={this.centerCameraPosition}
                                camera_position={this.state.camera_position}
                                center_position={this.state.center_position}
                            />
                        </Grid>
                        <Grid container xl={2} md={2} sm={2} xs={12}>
                            <Grid container xl={10} md={10} sm={10} xs={12}>
                                <Grid item xs={1}/>
                                <Grid item xl={12} md={12} sm={12} xs={10}>
                                    <p style={{fontSize: 16, margin: 0}}>Speed</p>
                                    <Slider
                                        value={this.state.speed}
                                        min={10}
                                        max={100}
                                        step={10}
                                        valueLabelDisplay="auto"
                                        marks={[
                                            {
                                                value: 10,
                                                label: '10%',
                                            },
                                            {
                                                value: 30,
                                                label: '30%',
                                            },
                                            {
                                                value: 50,
                                                label: '50%',
                                            },
                                            {
                                                value: 80,
                                                label: '80%',
                                            },
                                            {
                                                value: 100,
                                                label: '100%',
                                            }
                                            ]}
                                        onChange={this.updateSpeed}
                                        aria-label="Speed Slider" />
                                </Grid>
                                <Grid item xs={1}/>
                                <Grid item xs={1}/>
                                <Grid item xl={12} md={12} sm={12} xs={10}>
                                    <p style={{fontSize: 16, margin: 0}}>Distance (T/O {this.getDistanceTimeout().toFixed(1)}s)</p>
                                    <Slider
                                        value={this.state.distance}
                                        min={0}
                                        max={29}
                                        step={1}
                                        valueLabelDisplay="auto"
                                        valueLabelFormat={this.distanceLabelFormat}
                                        scale={this.calculateDistanceValue}
                                        marks={[
                                            {
                                                value: 0,
                                                label: '0mm',
                                            },
                                            {
                                                value: 10,
                                                label: '1cm',
                                            },
                                            {
                                                value: 20,
                                                label: '10cm',
                                            },
                                            {
                                                value: 29,
                                                label: '1m',
                                            }
                                            ]}
                                        onChange={this.updateDistance}
                                        aria-label="Distance Slider" />
                                </Grid>
                                <Grid item xs={1}/>
                                <Grid item xs={1}/>
                                <Grid item xl={12} md={12} sm={12} xs={10}>
                                <p style={{fontSize: 16, margin: 0}}>Rotation  (T/O {this.getRotationTimeout().toFixed(1)}s)</p>
                                <Slider
                                    value={this.state.rotation}
                                    min={1}
                                    max={90}
                                    step={1}
                                    valueLabelDisplay="auto"
                                    marks={[
                                        {
                                            value: 0,
                                            label: '0º',
                                        },
                                        {
                                            value: 10,
                                            label: '10º',
                                        },
                                        {
                                            value: 30,
                                            label: '30º',
                                        },
                                        {
                                            value: 45,
                                            label: '45º',
                                        },
                                        {
                                            value: 90,
                                            label: '90º',
                                        }
                                        ]}
                                    onChange={this.updateRotation}
                                    aria-label="Rotation Slider" />
                                </Grid>
                                <Grid item xs={1}/>
                                <Grid item xs={1}/>
                                <Grid item xs={1}/>
                                <DirectionCross
                                    forward_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD)}
                                    forward_slight_left_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_SLIGHT_LEFT)}
                                    forward_left_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_LEFT)}
                                    forward_slight_right_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_SLIGHT_RIGHT)}
                                    forward_right_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_RIGHT)}
                                    uturn_left_callback={this.moveRobot.bind(this, MOVE_INTENT_U_TURN_LEFT)}
                                    slight_uturn_left_callback={this.moveRobot.bind(this, MOVE_INTENT_SLIGHT_LEFT)}
                                    stop_callback={this.stopRobot}
                                    slight_uturn_right_callback={this.moveRobot.bind(this, MOVE_INTENT_SLIGHT_RIGHT)}
                                    uturn_right_callback={this.moveRobot.bind(this, MOVE_INTENT_U_TURN_RIGHT)}
                                    backward_callback={this.moveRobot.bind(this, MOVE_INTENT_BACKWARD)}
                                    backward_slight_left_callback={this.moveRobot.bind(this, MOVE_INTENT_BACKWARD_SLIGHT_LEFT)}
                                    backward_left_callback={this.moveRobot.bind(this, MOVE_INTENT_BACKWARD_LEFT)}
                                    backward_slight_right_callback={this.moveRobot.bind(this, MOVE_INTENT_BACKWARD_SLIGHT_RIGHT)}
                                    backward_right_callback={this.moveRobot.bind(this, MOVE_INTENT_BACKWARD_RIGHT)}
                                />
                            </Grid>
                            <Grid item xl={1} md={1} sm={1} xs={12}/>
                            <Grid item xl={1} md={1} sm={1} xs={12}/>
                            <Divider/>
                            <Grid item xl={12} md={12} sm={12} xs={12}>
                                <ArmControl
                                    hide={!this.config.robot_has_arm}
                                    position_claw={this.state.arm_position_claw}
                                    max_angle_claw={this.state.arm_max_angle_claw}
                                    move_claw_callback={this.moveArm.bind(this, "claw")}
                                    position_wrist={this.state.arm_position_wrist}
                                    max_angle_wrist={this.state.arm_max_angle_wrist}
                                    move_wrist_callback={this.moveArm.bind(this, "wrist")}
                                    lock_wrist_callback={this.setWristLock.bind(this, !this.state.lock_wrist)}
                                    lock_wrist={this.state.lock_wrist}
                                    position_forearm={this.state.arm_position_forearm}
                                    max_angle_forearm={this.state.arm_max_angle_forearm}
                                    move_forearm_callback={this.moveArm.bind(this, "forearm")}
                                    position_shoulder={this.state.arm_position_shoulder}
                                    max_angle_shoulder={this.state.arm_max_angle_shoulder}
                                    move_shoulder_callback={this.moveArm.bind(this, "shoulder")}
                                    move_to_position_callback={this.moveArmToPosition}
                                />
                            </Grid>
                        </Grid>
                    </Grid>
                </header>
            </div>
        );
    }
}

export default App;
