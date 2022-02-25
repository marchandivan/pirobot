import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import Stack from '@mui/material/Stack';
import TextField from "@material-ui/core/TextField";
import React from 'react';
import './App.css';
import DirectionCross from "./DirectionCross";
import ArmControl from "./ArmContorl"
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import IconButton from "@material-ui/core/IconButton";
import BackspaceIcon from '@mui/icons-material/Backspace';
import FlashlightOnIcon from '@mui/icons-material/FlashlightOn';
import FlashlightOffIcon from '@mui/icons-material/FlashlightOff';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import BrightnessHighIcon from '@mui/icons-material/BrightnessHigh';
import BrightnessMediumIcon from '@mui/icons-material/BrightnessMedium';
import BrightnessLowIcon from '@mui/icons-material/BrightnessLow';
import Divider from '@material-ui/core/Divider';
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FavoriteIcon from '@mui/icons-material/Favorite';

const KEY_UP = 38
const KEY_DOWN = 40
const KEY_LEFT = 37
const KEY_RIGHT = 39
const KEY_ESC = 27
const KEY_SPACE = 32
const KEY_0 = 48
const KEY_9 = 57
const KEY_PLUS = 187
const KEY_MINUS = 189

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
const MOVE_INTENT_RIGHT = 10
const MOVE_INTENT_LEFT = 11
const MOVE_INTENT_STOP = 11

class App extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            left_on: false,
            right_on: false,
            speed: 100,
            duration: 10.0,
            min_duration: 0.2,
            max_duration: 30.0,
            duration_step: 0.2,
            mouse_x: 0,
            mouse_y: 0,
            lcd_brightness: 100,
            mood: "relaxed",
            moods: ["relaxed"],
            arm_position_claw: 0,
            arm_position_wrist: 0,
            arm_position_forearm: 0,
            arm_position_shoulder: 0
        }
        this.key_down = {};
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
        } else if (event.keyCode === KEY_PLUS) {
            this.setState({
                duration: Math.round(Math.min(this.state.max_duration, this.state.duration + this.state.duration_step) * 10) / 10
            })
        } else if (event.keyCode === KEY_MINUS) {
            this.setState({
                duration: Math.round(Math.max(this.state.min_duration, this.state.duration - this.state.duration_step) * 10) / 10
            })
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
            move_intent = MOVE_INTENT_LEFT;
        } else if (this.key_down[KEY_RIGHT]) {
            move_intent = MOVE_INTENT_RIGHT;
        }

        this.moveRobot(move_intent);
    }

    updateState = (data) => {
        if (data.status === "OK") {
            this.setState({
                left_on: data.robot.light.left_on,
                right_on: data.robot.light.right_on,
                moods: data.robot.moods,
                arm_position_claw: data.robot.arm.position.claw,
                arm_max_angle_claw: data.robot.arm.config.claw.max_angle,
                arm_position_wrist: data.robot.arm.position.wrist,
                arm_max_angle_wrist: data.robot.arm.config.wrist.max_angle,
                arm_position_forearm: data.robot.arm.position.forearm,
                arm_max_angle_forearm: data.robot.arm.config.forearm.max_angle,
                arm_position_shoulder: data.robot.arm.position.shoulder,
                arm_max_angle_shoulder: data.robot.arm.config.shoulder.max_angle,
            });
        } else {
            console.error(data.message);
        }
    }

    updateSpeed = (event, value) => {
        this.setState({
            speed: value
        })
    }

    updateDuration = (event, value) => {
        this.setState({
            duration: value
        })
    }

    switchFrontLight = (event, checked) => {
        this.setLight (checked, checked);
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
            },
            body: JSON.stringify({
                x: this.state.mouse_x,
                y: this.state.mouse_y,
                speed: this.state.speed,
                timeout: this.state.duration
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
            },
            body: JSON.stringify({
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
        switch (move_intent) {
            case MOVE_INTENT_FORWARD:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_FORWARD_SLIGHT_LEFT:
                left_orientation = 'F';
                left_speed = 0.5;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_FORWARD_LEFT:
                left_orientation = 'F';
                left_speed = 0.0;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_FORWARD_SLIGHT_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.5;
                break;
            case MOVE_INTENT_FORWARD_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.0;
                break;
            case MOVE_INTENT_LEFT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_RIGHT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_BACKWARD:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_BACKWARD_SLIGHT_LEFT:
                left_orientation = 'B';
                left_speed = 0.5;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_BACKWARD_LEFT:
                left_orientation = 'B';
                left_speed = 0.0;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_BACKWARD_SLIGHT_RIGHT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.5;
                break;
            case MOVE_INTENT_BACKWARD_RIGHT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.0;
                break;
            case MOVE_INTENT_STOP:
            default:
                left_orientation = 'F';
                left_speed = 0.0;
                right_orientation ='F'
                right_speed = 0.0;
                break;
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
            },
            body: JSON.stringify({
                left_orientation: left_orientation,
                left_speed: left_speed * this.state.speed,
                right_orientation: right_orientation,
                right_speed: right_speed * this.state.speed,
                duration: this.state.duration
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
            },
            body: JSON.stringify({})
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    setLight = (left_on, right_on) => {
        let url = '/api/set_light/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                left_on: left_on,
                right_on: right_on
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

    captureImage = () => {
        let url = '/api/capture_image/';
        if(process.env.REACT_APP_API_URL) {
            url = process.env.REACT_APP_API_URL + url;
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                destination: "lcd"
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
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
            },
            body: JSON.stringify({
                id: id,
                angle: value
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
            },
            body: JSON.stringify({
                position_id: position_id
            })
        })
            .then(response => response.json())
            .then(data => this.updateState(data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    render() {
        return (
            <div className="App" >
                <header className="App-header">
                    <Grid container spacing={0} direction="row" justifyContent="center" alignItems="center">
                        <Grid item xl={2} md={2} sm={2} xs={12}>
                            <Grid container spacing={2}>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Front Light
                                    </p>
                                </Grid>
                                <Grid item xl={4} md={4} sm={4} xs={4}/>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.setLight.bind(this, false, false)}><FlashlightOffIcon/></IconButton>
                                </Grid>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.setLight.bind(this, true, true)}><FlashlightOnIcon/></IconButton>
                                </Grid>
                            </Grid>
                            <Divider/>
                            <Grid container>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Screen
                                    </p>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.resetLcdScreen}><BackspaceIcon/></IconButton>
                                </Grid>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.updateLcdBrightness.bind(this, 0)}><PowerSettingsNewIcon/></IconButton>
                                </Grid>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.updateLcdBrightness.bind(this, 20)}><BrightnessLowIcon/></IconButton>
                                </Grid>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.updateLcdBrightness.bind(this, 60)}><BrightnessMediumIcon/></IconButton>
                                </Grid>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.updateLcdBrightness.bind(this, 100)}><BrightnessHighIcon/></IconButton>
                                </Grid>
                            </Grid>
                            <Grid container>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={2} md={2} sm={2} xs={2}>
                                    <IconButton onClick={this.setLcdPicture.bind(this, "heart")}><FavoriteIcon/></IconButton>
                                </Grid>
                            </Grid>
                            <Grid container>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Mood
                                    </p>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={9} md={9} sm={9} xs={9}>
                                  <Select
                                    fullWidth
                                    value={this.state.mood}
                                    label="Age"
                                    onChange={this.updateMood}
                                  >
                                    {
                                        this.state.moods.map((mood) =>
                                        <MenuItem key={mood} value={mood}>{mood}</MenuItem>)
                                    }
                                  </Select>
                                </Grid>
                            </Grid>
                            <p/>
                            <Divider/>
                            <Grid container>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Say Something
                                    </p>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={11} md={11} sm={11} xs={11}>
                                    <TextField onKeyDown={this.keyPress} fullWidth={true}/>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item xl={8} md={8} sm={8} xs={12}>
                            <Grid item xl={12} md={12} sm={12} xs={12}>
                                <img
                                    src={(process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL : "") + "/api/stream/"}
                                    width="95%"
                                    alt="Camera Feed"
                                    onMouseMove={this.onMouseMove}
                                    onClick={this.onStreamClick}
                                />
                            </Grid>
                            <Grid item xl={12} md={12} sm={12} xs={12}>
                              <IconButton onClick={this.captureImage}><CameraAltIcon/></IconButton>
                            </Grid>
                        </Grid>
                        <Grid item xl={2} md={2} sm={2} xs={12}>
                            <Grid item xl={10} md={10} sm={10} xs={12}>
                                <p>Speed - Timeout</p>
                                <Stack spacing={1} direction="row" alignItems="center">
                                    <Slider
                                        value={this.state.speed}
                                        min={0}
                                        max={100}
                                        onChange={this.updateSpeed}
                                        aria-label="Speed Slider" />
                                    <p style={{fontSize: 16, width: 70}}>{this.state.speed}%</p>
                                </Stack>
                                <Stack spacing={1} direction="row" alignItems="center">
                                    <Slider
                                        value={this.state.duration}
                                        min={this.state.min_duration}
                                        max={this.state.max_duration}
                                        step={this.state.duration_step}
                                        onChange={this.updateDuration}
                                        aria-label="Duration Slider" />
                                    <p style={{fontSize: 16, width: 70}}>{this.state.duration}s</p>
                                </Stack>
                                <DirectionCross
                                    forward_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD)}
                                    forward_slight_left_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_SLIGHT_LEFT)}
                                    forward_left_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_LEFT)}
                                    forward_slight_right_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_SLIGHT_RIGHT)}
                                    forward_right_callback={this.moveRobot.bind(this, MOVE_INTENT_FORWARD_RIGHT)}
                                    uturn_left_callback={this.moveRobot.bind(this, MOVE_INTENT_LEFT)}
                                    stop_callback={this.stopRobot}
                                    uturn_right_callback={this.moveRobot.bind(this, MOVE_INTENT_RIGHT)}
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
                            <Grid item xl={10} md={10} sm={10} xs={12}>
                                <ArmControl
                                    position_claw={this.state.arm_position_claw}
                                    max_angle_claw={150}
                                    move_claw_callback={this.moveArm.bind(this, "claw")}
                                    position_wrist={this.state.arm_position_wrist}
                                    max_angle_wrist={this.state.arm_max_angle_wrist}
                                    move_wrist_callback={this.moveArm.bind(this, "wrist")}
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
