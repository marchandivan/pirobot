import React from 'react';
import SocketIO from 'socket.io-client';

import './App.css';
import VideoStreamControl from "./VideoStreamControl";

class App extends React.Component {
    socket = SocketIO.connect("http://localhost:5000");

    constructor(props) {
        super(props);
        this.state = {};
    }

    send_action = (type, action, args={}) => {
        this.socket.emit("message", {type: type, action: action,  args: args});
    }

    capture_image = () => {
        this.send_action("camera", "capture_picture")
    }

    stream_setup = () => {
    }

    render() {
      return (
        <div className="App">
          <header className="App-header">
              <VideoStreamControl
                  socket={this.socket}
                  send_action={this.send_action}
                  center_position={50}
              />
          </header>
        </div>
      );
    }
}

export default App;
