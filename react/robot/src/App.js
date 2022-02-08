import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import Switch from '@material-ui/core/Switch'
import FormControlLabel from '@material-ui/core/FormControlLabel'
import TextField from "@material-ui/core/TextField";
import React from 'react';
import './App.css';
import DirectionCross from "./DirectionCross";
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import IconButton from "@material-ui/core/IconButton";
import BackspaceIcon from '@mui/icons-material/Backspace';

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
const KEY_I = 73
const KEY_J = 74
const KEY_K = 76
const KEY_L = 77

const MOVE_KEYS = [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_I, KEY_J, KEY_K, KEY_L]

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
            duration: 2.0,
            min_duration: 0.2,
            max_duration: 30.0,
            duration_step: 0.2,
            mouse_x: 0,
            mouse_y: 0,
            lcd_brightness: 100
        };
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
        console.log("Key Down " + event.keyCode)
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
        console.log("Key Up " + event.keyCode)
        this.key_down[event.keyCode] = false;
    }

    moveKeyDown = () => {
        let move_intent = MOVE_INTENT_STOP;
        if (this.key_down[KEY_UP] || this.key_down[KEY_I]) {
            if (this.key_down[KEY_LEFT] || this.key_down[KEY_J]) {
                move_intent = MOVE_INTENT_FORWARD_LEFT;
            } else if (this.key_down[KEY_RIGHT] || this.key_down[KEY_L]) {
                move_intent = MOVE_INTENT_FORWARD_RIGHT;
            } else {
                move_intent = MOVE_INTENT_FORWARD
            }
        } else if (this.key_down[KEY_DOWN] || this.key_down[KEY_K]) {
            if (this.key_down[KEY_LEFT] || this.key_down[KEY_J]) {
                move_intent = MOVE_INTENT_BACKWARD_LEFT;
            } else if (this.key_down[KEY_RIGHT] || this.key_down[KEY_L]) {
                move_intent = MOVE_INTENT_BACKWARD_RIGHT;
            } else {
                move_intent = MOVE_INTENT_BACKWARD
            }
        } else if (this.key_down[KEY_LEFT] || this.key_down[KEY_J]) {
            move_intent = MOVE_INTENT_LEFT;
        } else if (this.key_down[KEY_RIGHT] || this.key_down[KEY_L]) {
            move_intent = MOVE_INTENT_RIGHT;
        }

        this.moveRobot(move_intent);
    }

    updateState = (data) => {
        this.setState({
            left_on: data.robot.light.left_on,
            right_on: data.robot.light.right_on
        });
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
        this.setState({ mouse_x: 100 * (e.clientX - e.target.x + 1) / e.target.width,
                              mouse_y: 100 * (e.clientY - e.target.y + 1) / e.target.height });
    }

    onStreamClick = (e) => {
        // Double click
        if (e.detail === 2) {
            this.selectTarget();
        }
    }

    selectTarget = (e) => {
        let url = '/api/select_target/';
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
                y: this.state.mouse_y
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
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.5;
                break;
            case MOVE_INTENT_FORWARD_LEFT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='F'
                right_speed = 0.0;
                break;
            case MOVE_INTENT_FORWARD_SLIGHT_RIGHT:
                left_orientation = 'F';
                left_speed = 0.5;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_FORWARD_RIGHT:
                left_orientation = 'F';
                left_speed = 0.0;
                right_orientation ='F'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_LEFT:
                left_orientation = 'F';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_RIGHT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='F'
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
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.5;
                break;
            case MOVE_INTENT_BACKWARD_LEFT:
                left_orientation = 'B';
                left_speed = 1.0;
                right_orientation ='B'
                right_speed = 0.0;
                break;
            case MOVE_INTENT_BACKWARD_SLIGHT_RIGHT:
                left_orientation = 'B';
                left_speed = 0.5;
                right_orientation ='B'
                right_speed = 1.0;
                break;
            case MOVE_INTENT_BACKWARD_RIGHT:
                left_orientation = 'B';
                left_speed = 0.0;
                right_orientation ='B'
                right_speed = 1.0;
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

    updateLcdBrightness = (event, value) => {
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

    render() {
        return (
            <div className="App" >
                <header className="App-header">
                    <Grid container spacing={0} direction="row" justifyContent="center" alignItems="center">
                        <Grid item xl={2} md={2} sm={2} xs={12}>
                            <Grid container spacing={2}>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <FormControlLabel control={<Switch onChange={this.switchFrontLight}/>} label="Front Light" />
                                </Grid>
                            </Grid>
                            <Grid container>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <p>
                                        Say Something
                                    </p>
                                </Grid>
                                <Grid item xl={12} md={12} sm={12} xs={12}>
                                    <TextField onKeyDown={this.keyPress} fullWidth={true}/>
                                </Grid>
                                <Grid item xl={1} md={1} sm={1} xs={1}/>
                                <Grid item xl={10} md={10} sm={10} xs={10}>
                                    <p>
                                        Screen Brightness
                                    </p>
                                    <Slider
                                        value={this.state.lcd_brightness}
                                        valueLabelDisplay="on"
                                        min={0}
                                        max={100}
                                        onChange={this.updateLcdBrightness}
                                        aria-label="Speed Slider" />
                                    <IconButton onClick={this.resetLcdScreen}><BackspaceIcon/></IconButton>
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
                            <Grid item xl={1} md={1} sm={1} xs={12}/>
                            <Grid item xl={10} md={10} sm={10} xs={12}>
                                <p>
                                    Speed
                                </p>
                                <Slider
                                    value={this.state.speed}
                                    valueLabelDisplay="on"
                                    min={0}
                                    max={100}
                                    onChange={this.updateSpeed}
                                    aria-label="Speed Slider" />
                                <p>
                                    Duration
                                </p>
                                <Slider
                                    value={this.state.duration}
                                    valueLabelDisplay="on"
                                    min={this.state.min_duration}
                                    max={this.state.max_duration}
                                    step={this.state.duration_step}
                                    onChange={this.updateDuration}
                                    aria-label="Duration Slider" />
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
                        </Grid>
                    </Grid>
                </header>
            </div>
        );
    }
}

export default App;
