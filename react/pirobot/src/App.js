import React from 'react';

import './App.css';
import VideoStreamControl from "./VideoStreamControl";


class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            ws: null,
            robot_config: {},
            robot_name: null,
            robot_status: {}
        };
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

    render() {
        document.body.style.overflow = "hidden";
        if (document.body.fullscreenEnabled) {
            document.body.requestFullscreen();
        }
        return (
        <div className="App">
            <VideoStreamControl
                  send_action={this.send_action}
                  center_position={50}
                  config={this.state.robot_config}
                  status={this.state.robot_status}
              />
        </div>
        );
    }
}

export default App;
